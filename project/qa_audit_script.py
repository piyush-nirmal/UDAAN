import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
from django.conf import settings
# modify allowed hosts before setup
if '*' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('*')
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

django.setup()

from django.test import Client
from django.urls import get_resolver, URLPattern, URLResolver
from django.contrib.auth import get_user_model

User = get_user_model()

def get_all_urls(urlpatterns, prefix=''):
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            route = str(pattern.pattern)
            route = route.replace('^', '').replace('$', '')
            full_url = prefix + route
            urls.append(full_url)
        elif isinstance(pattern, URLResolver):
            route = str(pattern.pattern)
            route = route.replace('^', '').replace('$', '')
            urls.extend(get_all_urls(pattern.url_patterns, prefix + route))
    return set(urls)

def run_phase1_2():
    print("--- PHASE 1 & 2: URL CRAWL & ACTION TESTING ---")
    urls = get_all_urls(get_resolver().url_patterns)
    c = Client()
    
    clean_urls = []
    for u in urls:
        if '<' in u or '(?P' in u: continue
        if u.startswith('ckeditor5/') or u.startswith('admin/'): continue
        if u.startswith('/'): clean_urls.append(u)
        else: clean_urls.append('/' + u)
        
    print(f"Testing {len(clean_urls)} static routes...")
    
    for u in sorted(set(clean_urls)):
        try:
            resp = c.get(u)
            status = resp.status_code
            print(f"{status} | GET {u}")
        except Exception as e:
            print(f"ERR | GET {u} -> {e}")

if __name__ == '__main__':
    run_phase1_2()
