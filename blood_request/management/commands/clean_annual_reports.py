"""
Tidies up the Annual Report records in the database WITHOUT removing years
that genuinely have no report uploaded yet (e.g. 2004-05 .. 2020-21). Those
are left exactly as they are -- the reports page shows "Unable to load
report" for them, which is correct.

The only thing this command touches: a couple of old data migrations left
duplicate rows for the SAME year (e.g. "2024-25", "2024-25_ZVvb9sh",
"2024-25_uZ2Hnwy" all pointing at copies of the same file, from when Django
auto-renamed re-uploaded files). For each year with more than one row, this
keeps a single row -- preferring one whose PDF is actually present on disk --
deletes the rest, and renames the title to the clean "YYYY-YY" form the site
displays.

    python manage.py clean_annual_reports            # show what would change
    python manage.py clean_annual_reports --apply    # actually change it
"""
import re

from django.core.management.base import BaseCommand

from blood_request.models import Report


def year_label(title):
    """Extract the 'YYYY-YY' label from a stored report title."""
    label = (title or "").strip()
    match = re.search(r"(\d{4}-\d{2})", label)
    return match.group(1) if match else label


class Command(BaseCommand):
    help = (
        "Merge duplicate Annual Report rows for the same year and tidy their "
        "titles. Never deletes a year that has no report at all."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the changes. Without this flag the command is a dry run.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        def file_exists(report):
            if not report.file:
                return False
            try:
                return report.file.storage.exists(report.file.name)
            except Exception:
                return False

        by_year = {}
        duplicates = []
        renames = []

        for report in Report.objects.all().order_by("-published_date", "-id"):
            label = year_label(report.title)

            if label not in by_year:
                by_year[label] = report
                continue

            # Already have a row for this year -- keep whichever one has a
            # working file, delete the other.
            current = by_year[label]
            if not file_exists(current) and file_exists(report):
                duplicates.append(current)
                by_year[label] = report
            else:
                duplicates.append(report)

        for label, report in by_year.items():
            if report.title.strip() != label:
                renames.append((report, label))

        for report in duplicates:
            self.stdout.write(self.style.WARNING(
                f"[duplicate year] '{report.title}' (file: {report.file.name or '(none)'})"
            ))

        for report, label in renames:
            self.stdout.write(
                f"[rename]         '{report.title}' -> '{label}'"
            )

        kept_missing = [r for r in by_year.values() if not file_exists(r)]
        if kept_missing:
            self.stdout.write(self.style.NOTICE(
                f"\n{len(kept_missing)} year(s) kept with no report file on disk "
                f"(these will show 'Unable to load report' on the site -- left as-is):"
            ))
            for r in sorted(kept_missing, key=lambda r: year_label(r.title), reverse=True):
                self.stdout.write(f"   {year_label(r.title)}")

        if not apply_changes:
            self.stdout.write(self.style.NOTICE(
                f"\nDry run: {len(duplicates)} duplicate row(s) to remove, "
                f"{len(renames)} title(s) to clean up. Re-run with --apply to make these changes."
            ))
            return

        for report in duplicates:
            report.delete()

        for report, label in renames:
            report.title = label
            report.save(update_fields=["title"])

        self.stdout.write(self.style.SUCCESS(
            f"\nRemoved {len(duplicates)} duplicate row(s), renamed {len(renames)}. "
            f"{Report.objects.count()} reports remain."
        ))
