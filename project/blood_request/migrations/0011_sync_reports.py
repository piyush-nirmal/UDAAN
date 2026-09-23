from django.db import migrations
from django.conf import settings
import os
from datetime import date

def sync_reports(apps, schema_editor):
    Report = apps.get_model('blood_request', 'Report')
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    
    if not os.path.exists(reports_dir):
        return

    for filename in os.listdir(reports_dir):
        if filename.lower().endswith('.pdf'):
            # Check if exists
            relative_path = f"reports/{filename}"
            if not Report.objects.filter(file=relative_path).exists():
                # Parse year
                title = filename.replace('.pdf', '')
                published_date = date.today() # fallback
                
                # specific logic for "YYYY-YY.pdf"
                try:
                    parts = title.split('-')
                    if len(parts) == 2 and len(parts[0]) == 4:
                        start_year = int(parts[0])
                        published_date = date(start_year + 1, 3, 31)
                        title = f"Annual Report {title}"
                except ValueError:
                    pass

                Report.objects.create(
                    title=title,
                    file=relative_path,
                    published_date=published_date
                )

class Migration(migrations.Migration):
    dependencies = [
        ("blood_request", "0010_populate_reports"),
    ]

    operations = [
        migrations.RunPython(sync_reports),
    ]
