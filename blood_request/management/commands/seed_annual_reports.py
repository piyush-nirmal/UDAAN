"""
Attaches the real annual report PDFs (placed in media/reports/) to Report
records in the database, creating the record if it doesn't exist yet, or
fixing it if it exists but points to a missing/broken file.

Run this once after copying the PDFs into media/reports/:

    python manage.py seed_annual_reports

This only touches the specific years listed below. Every other year
already in the database is left exactly as-is, so if its file is
genuinely missing, the page will keep showing "Unable to load report"
for that year -- which is the correct behavior for a year with no
report on file.
"""
from datetime import date

from django.core.files import File
from django.core.management.base import BaseCommand

from blood_request.models import Report

# (report title as it should appear on the site, filename under media/reports/, published_date)
REPORTS_TO_FIX = [
    ("2021-22", "2021-22.pdf", date(2022, 4, 1)),
    ("2022-23", "2022-23.pdf", date(2023, 4, 1)),
    ("2023-24", "2023-24.pdf", date(2024, 4, 1)),
    ("2024-25", "2024-25.pdf", date(2025, 4, 1)),
]


class Command(BaseCommand):
    help = "Attach the real annual report PDFs to their Report DB records."

    def handle(self, *args, **options):
        import os
        from django.conf import settings

        for title, filename, published_date in REPORTS_TO_FIX:
            file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f"Skipping '{title}': {file_path} not found on disk."
                ))
                continue

            report, created = Report.objects.get_or_create(
                title=title,
                defaults={"published_date": published_date},
            )

            with open(file_path, "rb") as f:
                report.file.save(filename, File(f), save=False)

            report.published_date = published_date
            report.save()

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} report '{title}' -> {filename}"))

        self.stdout.write(self.style.SUCCESS("Done."))
