import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django
django.setup()

from blood_request.models import (
    Blog,
    Campaign,
    Project,
    Activity,
    Announcement,
    JobPosting,
    Testimonial,
    NewsClipping,
    CampusAmbassador,
    Report,
    PolicyReport,
)


class DjangoKnowledgeLoader:

    def load_blogs(self):
        documents = []

        for blog in Blog.objects.all():

            content = blog.content or blog.description or ""

            documents.append({
                "source": "Blog",
                "title": blog.title,
                "text": f"""
    Title:
    {blog.title}

    Description:
    {blog.description or ""}

    Content:
    {content}
    """
            })

        return documents


    def load_campaigns(self):
        documents = []

        for campaign in Campaign.objects.all():

            documents.append({
                "source": "Campaign",
                "title": campaign.title,
                "text": f"""
Campaign:
{campaign.title}

Description:
{campaign.description}

Beneficiaries:
{campaign.beneficiary_text}
"""
            })

        return documents

    def load_projects(self):
        documents = []

        for project in Project.objects.all():

            documents.append({
                "source": "Project",
                "title": project.title,
                "text": f"""
Project:
{project.title}

Description:
{project.description}

Content:
{project.content}
"""
            })

        return documents

    def load_activities(self):
        documents = []

        for activity in Activity.objects.filter(is_active=True):

            documents.append({
                "source": "Activity",
                "title": activity.title,
                "text": f"""
Activity:
{activity.title}

Description:
{activity.description}

Date:
{activity.date}
"""
            })

        return documents

    def load_announcements(self):
        documents = []

        for item in Announcement.objects.filter(is_active=True):

            documents.append({
                "source": "Announcement",
                "title": item.title,
                "text": f"""
Announcement:
{item.title}

Content:
{item.content}
"""
            })

        return documents

    def load_jobs(self):
        documents = []

        for job in JobPosting.objects.filter(is_active=True):

            documents.append({
                "source": "Job",
                "title": job.title,
                "text": f"""
Job:
{job.title}

Location:
{job.location}

Description:
{job.description}

Responsibilities:
{job.responsibilities}

Desired Profile:
{job.desired_profile}
"""
            })

        return documents

    def load_testimonials(self):
        documents = []

        for t in Testimonial.objects.filter(is_active=True):

            documents.append({
                "source": "Testimonial",
                "title": t.author,
                "text": f"""
Author:
{t.author}

Role:
{t.role}

Story:
{t.detailed_text or t.text}
"""
            })

        return documents

    def load_news(self):
        documents = []

        for news in NewsClipping.objects.all():

            documents.append({
                "source": "News",
                "title": news.title,
                "text": f"""
Title:
{news.title}

Newspaper:
{news.newspaper}

Summary:
{news.summary}
"""
            })

        return documents

    def load_ambassadors(self):
        documents = []

        for a in CampusAmbassador.objects.all():

            documents.append({
                "source": "Campus Ambassador",
                "title": a.name,
                "text": f"""
Name:
{a.name}

College:
{a.college}

City:
{a.city}

Description:
{a.description}
"""
            })

        return documents

    def load_everything(self):

        docs = []

        docs.extend(self.load_blogs())
        docs.extend(self.load_campaigns())
        docs.extend(self.load_projects())
        docs.extend(self.load_activities())
        docs.extend(self.load_announcements())
        docs.extend(self.load_jobs())
        docs.extend(self.load_testimonials())
        docs.extend(self.load_news())
        docs.extend(self.load_ambassadors())

        return docs


if __name__ == "__main__":

    loader = DjangoKnowledgeLoader()

    docs = loader.load_everything()

    print(f"\nLoaded {len(docs)} documents\n")

    for doc in docs[:5]:
        print("=" * 70)
        print(doc["source"])
        print(doc["title"])
        print(doc["text"][:400])