from django.db import migrations
import re


IMAGE_EXTENSIONS_RE = re.compile(r'(?i)(\\.(?:png|jpe?g|webp))+$')


def clean_blog_titles(apps, schema_editor):
    Blog = apps.get_model('blood_request', 'Blog')

    for blog in Blog.objects.all().only('id', 'title'):
        title = (blog.title or '').strip()
        cleaned = IMAGE_EXTENSIONS_RE.sub('', title).strip()

        # Also collapse accidental whitespace around the cleaned title.
        cleaned = re.sub(r'\\s+', ' ', cleaned)

        if cleaned and cleaned != title:
            Blog.objects.filter(pk=blog.pk).update(title=cleaned)


class Migration(migrations.Migration):

    dependencies = [
        ('blood_request', '0058_blood_donation_partner_models'),
    ]

    operations = [
        migrations.RunPython(clean_blog_titles, migrations.RunPython.noop),
    ]
