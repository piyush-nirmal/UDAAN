"""
Removes duplicate Blog rows created by an old data migration that made one
Blog per file under media/blogs/, including Django's auto-renamed duplicate
copies of re-uploaded images (e.g. "photo.jpg" and "photo_XY4qqIz.jpg" are
byte-identical). A later migration tried to de-duplicate by exact title
match, but since the random filename suffix makes every duplicate's
auto-generated title different, it never caught these.

This command groups Blog rows by the actual content (hash) of their image
file, keeps the oldest row in each group, and deletes the rest.

    python manage.py clean_duplicate_blogs            # show what would change
    python manage.py clean_duplicate_blogs --apply    # actually change it
"""
import hashlib

from django.core.management.base import BaseCommand

from blood_request.models import Blog


class Command(BaseCommand):
    help = "Remove duplicate Blog rows whose image file is byte-identical to an older one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write the changes. Without this flag the command is a dry run.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        def image_hash(blog):
            if not blog.image:
                return None
            try:
                with blog.image.open('rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
            except Exception:
                return None

        seen = {}
        duplicates = []

        for blog in Blog.objects.all().order_by('created_at', 'id'):
            h = image_hash(blog)
            if h is None:
                continue
            if h in seen:
                duplicates.append(blog)
            else:
                seen[h] = blog

        for blog in duplicates:
            self.stdout.write(self.style.WARNING(
                f"[duplicate] '{blog.title}' (image: {blog.image.name})"
            ))

        if not apply_changes:
            self.stdout.write(self.style.NOTICE(
                f"\nDry run: {len(duplicates)} duplicate blog(s) to remove. "
                f"Re-run with --apply to make these changes."
            ))
            return

        for blog in duplicates:
            blog.delete()

        self.stdout.write(self.style.SUCCESS(
            f"\nRemoved {len(duplicates)} duplicate blog(s). "
            f"{Blog.objects.count()} blogs remain."
        ))
