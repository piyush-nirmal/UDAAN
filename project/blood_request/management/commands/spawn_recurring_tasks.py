"""
Management command to auto-clone recurring tasks.
Run daily: python manage.py spawn_recurring_tasks
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from blood_request.models import Task


class Command(BaseCommand):
    help = 'Clones recurring tasks that are due for a new cycle.'

    def handle(self, *args, **options):
        today = date.today()
        recurring_tasks = Task.objects.filter(
            recurrence_rule__in=['daily', 'weekly', 'biweekly', 'monthly'],
            status='Done',
        )

        created_count = 0
        for task in recurring_tasks:
            anchor = task.last_recurred_at or (task.due_date or task.created_at.date())
            next_due = self._next_due(anchor, task.recurrence_rule)

            if next_due and next_due <= today:
                Task.objects.create(
                    project=task.project,
                    title=task.title,
                    description=task.description,
                    assigned_to=task.assigned_to,
                    status='To Do',
                    priority=task.priority,
                    due_date=next_due,
                    recurrence_rule=task.recurrence_rule,
                )
                task.last_recurred_at = today
                task.save(update_fields=['last_recurred_at'])
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created_count} recurring task(s).'
        ))

    @staticmethod
    def _next_due(anchor, rule):
        deltas = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'biweekly': timedelta(weeks=2),
            'monthly': timedelta(days=30),
        }
        delta = deltas.get(rule)
        return anchor + delta if delta else None
