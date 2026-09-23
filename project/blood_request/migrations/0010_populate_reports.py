from django.db import migrations
from datetime import date

def populate_reports(apps, schema_editor):
    Report = apps.get_model('blood_request', 'Report')
    
    # List of files identified in the reports/pdf folder
    report_years = [
        "2004-05", "2005-06", "2006-07", "2007-08", "2008-09", "2009-10",
        "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16",
        "2016-17", "2017-18", "2018-19", "2020-21"
    ]

    for year_str in report_years:
        parts = year_str.split('-')
        start_year = int(parts[0])
        end_year = start_year + 1
        published_date = date(end_year, 3, 31)

        Report.objects.create(
            title=f"Annual Report {year_str}",
            file=f"reports/{year_str}.pdf",
            published_date=published_date
        )

class Migration(migrations.Migration):
    dependencies = [
        ("blood_request", "0009_populate_projects"),
    ]

    operations = [
        migrations.RunPython(populate_reports),
    ]
