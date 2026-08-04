import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from .models import Task, BloodRequest

logger = logging.getLogger(__name__)


def _get_manager_emails():
    """
    Safely retrieves emails for all users in the 'Managers' group.
    Returns an empty list if the group does not exist, with a warning logged.
    Never raises Group.DoesNotExist.
    """
    managers_group = Group.objects.filter(name='Managers').first()
    if managers_group is None:
        logger.warning(
            "Signals > 'Managers' group does not exist. "
            "Skipping manager notification. Create the group in Django Admin."
        )
        return []
    return [u.email for u in managers_group.user_set.all() if u.email]


@receiver(post_save, sender=Task)
def notify_task_assignment(sender, instance, created, **kwargs):
    """
    Emails the assigned user immediately when a task is assigned.
    Email failures are logged but never interrupt the request.
    """
    if instance.assigned_to and instance.assigned_to.email:
        subject = f"New Task Assigned: {instance.title}"
        message = (
            f"Hello {instance.assigned_to.username},\n\n"
            f"You have been assigned a new task.\n\n"
            f"Title: {instance.title}\n"
            f"Priority: {instance.priority}\n"
            f"Due Date: {instance.due_date}\n\n"
            f"Please log in to the portal to view details."
        )

        logger.info(f"Signals > Sending Assignment Email to {instance.assigned_to.email}...")
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org',
                [instance.assigned_to.email],
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Signals > Failed to send task assignment email: {e}")


@receiver(post_save, sender=BloodRequest)
def notify_managers_blood_request(sender, instance, created, **kwargs):
    """
    Emails all Managers when a public Blood Request is received.
    Gracefully skips notifications if the Managers group is absent.
    Blood request creation always succeeds regardless of notification state.
    """
    if not created:
        return

    emails = _get_manager_emails()

    if not emails:
        logger.info("Signals > No manager emails found; skipping blood request notification.")
        return

    subject = f"URGENT: New Blood Request ({instance.blood_group})"
    message = (
        f"A new blood request has been submitted.\n\n"
        f"Patient Name: {instance.contact_person}\n"
        f"Blood Group: {instance.blood_group}\n"
        f"Units Needed: {instance.units}\n"
        f"City: {instance.city}\n"
        f"Phone: {instance.contact_phone}\n\n"
        f"Please contact them immediately."
    )

    logger.info(f"Signals > Alerting {len(emails)} Managers about Blood Request...")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org',
            emails,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Signals > Failed to send manager blood request alert: {e}")


from .models import Interaction


@receiver(post_save, sender=Interaction)
def auto_create_followup_task(sender, instance, created, **kwargs):
    """
    Automatically creates a Task if the Interaction outcome is 'Follow-up Scheduled'.
    """
    if created and instance.outcome == 'Follow-up Scheduled' and instance.next_followup_date:
        task_title = f"Follow-up: {instance.interaction_type} with {instance.entity}"
        logger.info(f"Signals > Auto-generating Follow-up Task for {instance.staff.username}...")

        Task.objects.create(
            title=task_title,
            description=f"Auto-generated from Interaction.\nNotes: {instance.notes}",
            assigned_to=instance.staff,
            due_date=instance.next_followup_date,
            priority='High',
            status='To Do'
        )


# --- Phase 29: Task Automation Rule Executor ---
from .models import TaskAutomationRule, Notification


@receiver(post_save, sender=Task)
def execute_automation_rules(sender, instance, created, **kwargs):
    """
    Checks all active TaskAutomationRules and fires matching actions
    when a Task is created or its status/priority changes.
    """
    rules = TaskAutomationRule.objects.filter(is_active=True)

    for rule in rules:
        triggered = False

        # Check trigger conditions
        if rule.trigger_type == 'task_created' and created:
            triggered = True
        elif rule.trigger_type == 'status_changed_done' and instance.status == 'Done':
            triggered = True
        elif rule.trigger_type == 'status_changed_in_progress' and instance.status == 'In Progress':
            triggered = True
        elif rule.trigger_type == 'priority_set_critical' and instance.priority == 'Critical':
            triggered = True
        # 'task_overdue' is handled by a cron/management command, not a signal

        if not triggered:
            continue

        logger.info(f"Automation > Rule '{rule.name}' triggered for Task '{instance.title}'")

        # Execute action
        try:
            if rule.action_type == 'send_email_assignee':
                if instance.assigned_to and instance.assigned_to.email:
                    try:
                        send_mail(
                            f"[Automation] {rule.name}: {instance.title}",
                            f"Task '{instance.title}' triggered automation rule: {rule.name}.\n\nStatus: {instance.status}\nPriority: {instance.priority}",
                            settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org',
                            [instance.assigned_to.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Automation > Email to assignee failed: {e}")

            elif rule.action_type == 'send_email_manager':
                # Use safe helper - never raises Group.DoesNotExist
                manager_emails = _get_manager_emails()
                if manager_emails:
                    try:
                        send_mail(
                            f"[Automation] {rule.name}: {instance.title}",
                            f"Task '{instance.title}' triggered automation rule: {rule.name}.\n\nAssigned to: {instance.assigned_to}\nStatus: {instance.status}\nPriority: {instance.priority}",
                            settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org',
                            manager_emails,
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Automation > Email to managers failed: {e}")

            elif rule.action_type == 'create_notification':
                # Notify the assignee OR the target user
                notify_user = rule.target_user or instance.assigned_to
                if notify_user:
                    Notification.objects.create(
                        user=notify_user,
                        message=f"[Auto] {rule.name}: Task '{instance.title}' ({instance.status})",
                        link=f"/admin/portal/task/{instance.id}/"
                    )

            elif rule.action_type == 'auto_assign_user':
                if rule.target_user and instance.assigned_to != rule.target_user:
                    # Avoid infinite recursion by using update() instead of save()
                    Task.objects.filter(pk=instance.pk).update(assigned_to=rule.target_user)
                    logger.info(f"Automation > Auto-assigned task to {rule.target_user.username}")

        except Exception as e:
            logger.error(f"Automation > Error executing rule '{rule.name}': {e}")

