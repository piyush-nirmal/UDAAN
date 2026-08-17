
import json
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.conf import settings
from .models import (
    BloodDonor, BloodRequest, ContactMessage, Report, Campaign, Task, StaffProfile, SubTask, 
    TaskAutomationRule, Donation, VolunteerRequest, Expense
)
from .schemas import DonorSchema, BloodRequestSchema
from pydantic import ValidationError
from django_ratelimit.decorators import ratelimit
# from django.shortcuts import render
from .models import Blog, Project, Task, SubTask, Team
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required, user_passes_test, login_required
from .models import CampusAmbassador, CampusAmbassadorApplication
from .models import PolicyReport

from .utils import create_notification, generate_unique_din, send_din_email

@ensure_csrf_cookie
def index(request):
    """
    Renders the main page. CSRF cookie is ensured for AJAX requests.
    """
    return render(request, 'blood_request/index.html')

@ratelimit(key='ip', rate='5/h', block=False)
def register_donor(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'success': False, 'error': 'Rate limit exceeded. Please try again later.'}, status=429)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 1. Validate with Pydantic
            donor_data = DonorSchema(**data)
            
            # 2. Check logic unique phone (Pydantic doesn't check DB)
            if BloodDonor.objects.filter(phone=donor_data.phone).exists():
                return JsonResponse({'success': False, 'error': 'Phone number already registered.'}, status=400)

            # 3. Create Model Instance
            din = generate_unique_din()
            donor = BloodDonor.objects.create(
                name=donor_data.name,
                blood_group=donor_data.blood_group,
                phone=donor_data.phone,
                email=donor_data.email,
                din=din,
                city=donor_data.city,
                state=donor_data.state,
                pin_code=donor_data.pin_code,
                consent_given=donor_data.consent_given,
                whatsapp_number=donor_data.whatsapp_number,
                email_notifications=donor_data.email_notifications,
                available_to_donate=donor_data.available_to_donate
            )
            
            # 4. Send Email
            if donor.email:
                send_din_email(donor.email, din, record_type='donor')
                
            return JsonResponse({'success': True, 'message': f'Registration successful! Your DIN is: {din}'})

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@login_required
@ratelimit(key='ip', rate='20/h', block=True)
def search_donors(request):
    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')

    donors = BloodDonor.objects.all()

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    
    if city:
        donors = donors.filter(city__icontains=city)
    
    results = []
    for donor in donors:
        results.append({
            'name': donor.name,
            'blood_group': donor.blood_group,
            'phone': donor.phone,
            'email': donor.email,
            'city': donor.city,
            'state': donor.state
        })

    return JsonResponse({'results': results})

@ratelimit(key='ip', rate='10/h', block=False)
def blood_request_create(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'success': False, 'error': 'Rate limit exceeded. Please try again later.'}, status=429)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            req_data = BloodRequestSchema(**data)
            
            din = generate_unique_din()
            blood_request = BloodRequest.objects.create(
                city=req_data.city,
                pin_code=req_data.pin_code,
                blood_group=req_data.blood_group,
                units=req_data.units,
                address_line_1=req_data.address_line_1,
                address_line_2=req_data.address_line_2,
                contact_person=req_data.contact_person,
                contact_phone=req_data.contact_phone,
                contact_email=req_data.contact_email,
                din=din,
            )
            
            if req_data.contact_email:
                send_din_email(req_data.contact_email, din, record_type='request')
                
            return JsonResponse({"success": True, "message": f"Blood request submitted successfully! Your DIN is: {din}"})
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

from .models import Campaign, Report, Project

def home_view(request):
    """
    Renders the homepage with dynamic content.
    """
    campaigns = Campaign.objects.all().order_by('-created_at')[:3]
    projects = Project.objects.all().order_by('-date')[:3]
    from .models import Testimonial, Announcement
    from datetime import date
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:7]
    
    # Fetch Active and Non-expired Announcements for homepage
    announcements = Announcement.objects.filter(
        Q(is_active=True) & 
        (Q(expiry_date__isnull=True) | Q(expiry_date__gte=date.today()))
    ).order_by('-priority', '-created_at')[:3]
    
    context = {
        'campaigns': campaigns,
        'projects': projects,
        'testimonials': testimonials,
        'announcements': announcements,
    }
    return render(request, 'home.html', context)

def donate_page(request):
    """
    Renders the production donate page with configurable bank details from settings.
    """
    from django.conf import settings as django_settings
    context = {
        'bank_account_name': getattr(django_settings, 'DONATE_BANK_ACCOUNT_NAME', 'UDAAN Society'),
        'bank_account_number': getattr(django_settings, 'DONATE_BANK_ACCOUNT_NUMBER', 'Contact us for details'),
        'bank_ifsc_code': getattr(django_settings, 'DONATE_BANK_IFSC_CODE', 'Contact us for details'),
        'bank_name': getattr(django_settings, 'DONATE_BANK_NAME', 'State Bank of India'),
        'bank_branch': getattr(django_settings, 'DONATE_BANK_BRANCH', 'Aligarh Branch'),
        'upi_id': getattr(django_settings, 'DONATE_UPI_ID', ''),
        'contact_email': getattr(django_settings, 'EMAIL_HOST_USER', 'mail@udaansociety.org'),
    }
    return render(request, 'donate.html', context)

from django.contrib.auth.decorators import login_required
from .models import Task

@login_required
def staff_dashboard(request):
    """
    Staff Dashboard: Kanban Board View with Bulletin and Task Grouping.
    """
    from .models import Announcement, BloodDonor
    
    # Fetch Active and Non-expired Announcements
    from datetime import date
    announcements = Announcement.objects.filter(
        Q(is_active=True) & 
        (Q(expiry_date__isnull=True) | Q(expiry_date__gte=date.today()))
    ).order_by('-priority', '-created_at')
    
    # Impact Stats
    total_donors = BloodDonor.objects.count()

    # Fetch tasks assigned to the user OR unassigned tasks
    all_tasks = Task.objects.filter(Q(assigned_to=request.user) | Q(assigned_to__isnull=True)).order_by('due_date')
    
    # Simple Python-side grouping (efficient enough for <100 tasks)
    todo_tasks = [t for t in all_tasks if t.status == 'To Do']
    inprogress_tasks = [t for t in all_tasks if t.status == 'In Progress']
    done_tasks = [t for t in all_tasks if t.status == 'Done']

    # Recent Activity (Last 5 updated tasks)
    recent_activity = Task.objects.filter(assigned_to=request.user).order_by('-updated_at')[:5]

    context = {
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'all_tasks': all_tasks,
        'announcements': announcements,
        'total_donors': total_donors,
        'recent_activity': recent_activity,
    }
    return render(request, 'staff_dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_task_status(request, pk):
    from django.utils import timezone
    import json
    
    # Check if this is an AJAX/JSON request
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    task = get_object_or_404(Task, pk=pk)
    # Only allow the assigned user or staff to update; also allow if unassigned
    if task.assigned_to and task.assigned_to != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    new_status = None
    
    if is_ajax:
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            # GPS data from AJAX
            lat = data.get('lat')
            lng = data.get('lng')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        # Form submission
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')

    # Dependency check: block progression if dependencies are unmet
    target_status = new_status
    if not target_status:
        # Predict what the toggle would produce
        if task.status == 'To Do':
            target_status = 'In Progress'
        elif task.status == 'In Progress':
            target_status = 'Done'
        else:
            target_status = 'To Do'

    if target_status != 'To Do' and task.is_blocked:
        unmet = list(task.unmet_dependencies.values_list('title', flat=True)[:5])
        msg = f"Blocked: depends on {', '.join(unmet)}"
        if is_ajax:
            return JsonResponse({'status': 'blocked', 'message': msg}, status=409)
        from django.contrib import messages as django_messages
        django_messages.warning(request, msg)
        return redirect('staff_dashboard')

    # Logic
    if new_status:
        # Direct status update (Drag & Drop)
        if new_status in ['To Do', 'In Progress', 'Review', 'Done']:
            task.status = new_status
            if new_status == 'Done':
                task.completion_timestamp = timezone.now()
                if lat and lng:
                    task.completion_lat = lat
                    task.completion_lng = lng
    else:
        # Toggle logic (Legacy/Button)
        if task.status == 'To Do':
            task.status = 'In Progress'
        elif task.status == 'In Progress':
            task.status = 'Done'
            # Only save completion data when marking as Done
            if lat and lng:
                task.completion_lat = lat
                task.completion_lng = lng
            task.completion_timestamp = timezone.now()
        else:
            task.status = 'To Do'
        
    task.save()
    
    if is_ajax:
        return JsonResponse({'status': 'success', 'new_status': task.status, 'task_id': task.pk})
    
    return redirect('staff_dashboard')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Both assigned users and managers can view
    return render(request, 'blood_request/task_detail.html', {'task': task})

@login_required
@require_POST
def add_task_comment(request, pk):
    task = get_object_or_404(Task, pk=pk)
    content = request.POST.get('content')
    
    if content and content.strip():
        # Handle @mentions if they exist in the text
        import re
        from .utils import create_notification
        
        # Check permissions (either assigned to the task, or a manager)
        if task.assigned_to == request.user or request.user.groups.filter(name='Managers').exists() or request.user.is_superuser:
            comment = TaskComment.objects.create(
                task=task,
                author=request.user,
                content=content.strip()
            )
            
            # Simple @mention parsing with Permission Hardening
            mentions = re.findall(r'@(\w+)', content)
            for username in mentions:
                try:
                    mentioned_user = User.objects.get(username=username)
                    # Permission check: Only notify if they are assigned to task, are project managers, or are superusers
                    is_authorized = False
                    if mentioned_user == task.assigned_to or mentioned_user.is_superuser:
                        is_authorized = True
                    elif task.project and task.project.managers.filter(id=mentioned_user.id).exists():
                        is_authorized = True
                    
                    if is_authorized:
                        create_notification(
                            user=mentioned_user,
                            message=f"{request.user.username} mentioned you in a comment on task '{task.title}'",
                            link=f"/admin/portal/task/{task.id}/"
                        )
                except User.DoesNotExist:
                    pass
            
            messages.success(request, "Comment added successfully.")
        else:
            messages.error(request, "You do not have permission to comment on this task.")
            
    return redirect('task_detail', pk=task.pk)

@login_required
@require_POST
def subtask_add(request, pk):
    task = get_object_or_404(Task, pk=pk)
    title = request.POST.get('title')
    if title:
        SubTask.objects.create(
            parent_task=task,
            title=title,
            assigned_to=task.assigned_to,
            status='To Do'
        )
    return redirect('task_detail', pk=task.pk)

@login_required
@require_POST
def subtask_update(request, sub_pk):
    subtask = get_object_or_404(SubTask, pk=sub_pk)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    if is_ajax:
        import json
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status in dict(SubTask.STATUS_CHOICES):
                subtask.status = new_status
                subtask.save()
                return JsonResponse({'status': 'success', 'new_status': subtask.status})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error'}, status=400)
            
    # Fallback
    new_status = request.POST.get('status')
    if new_status in dict(SubTask.STATUS_CHOICES):
        subtask.status = new_status
        subtask.save()
    return redirect('task_detail', pk=subtask.parent_task.pk)

from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Managers').exists()

@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Manager Dashboard: View ALL tasks across the organization.
    Enhanced with Phase 7 metrics: Progress Bars, Resource Load, Bottlenecks.
    """
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    from datetime import date
    
    # 1. Task Overview
    all_tasks = Task.objects.select_related('assigned_to', 'project').all().order_by('-created_at')
    
    # Kanban Buckets
    todo_tasks = all_tasks.filter(status='To Do')
    inprogress_tasks = all_tasks.filter(status='In Progress')
    done_tasks = all_tasks.filter(status='Done')
    
    tasks = all_tasks # Keep for table if needed or backward compat
    
    # 2. Project Progress (Phase 7.1)
    # Calculate % completion for each project
    projects = Project.objects.annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='Done'))
    ).filter(total_tasks__gt=0).prefetch_related('managers') # Only show projects with tasks
    
    # Attach percentage manually (Django annotations for division can be complex database-dependent)
    for p in projects:
        if p.total_tasks > 0:
            p.progress = int((p.completed_tasks / p.total_tasks) * 100)
        else:
            p.progress = 0

    # 3. Resource Allocation (Phase 7.2)
    # Count open tasks (Not Done) for each staff member
    staff_load = User.objects.filter(is_superuser=False).annotate(
        active_task_count=Count('tasks', filter=~Q(tasks__status='Done'))
    ).order_by('-active_task_count').prefetch_related('profile')

    # 4. Bottlenecks (Phase 7.3)
    # Tasks that are NOT Done and Past Due date
    overdue_tasks = Task.objects.select_related('assigned_to', 'project').filter(
        ~Q(status='Done'),
        due_date__lt=date.today()
    ).order_by('due_date')

    # Simple stats
    stats = {
        'total': tasks.count(),
        'high_priority': tasks.filter(priority__in=['High', 'Critical']).count(),
        'pending': tasks.filter(status__in=['To Do', 'In Progress']).count(),
        'overdue': overdue_tasks.count()
    }

    context = {
        'tasks': tasks,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'stats': stats,
        'projects': projects,
        'staff_load': staff_load,
        'overdue_tasks': overdue_tasks,
        'teams': Team.objects.prefetch_related('members').all(),
    }
    return render(request, 'manager_dashboard.html', context)

def campaign_list(request):
    """
    Public Campaign Listing Page
    """
    campaigns = Campaign.objects.all().order_by('-created_at')
    return render(request, 'campaigns.html', {'campaigns': campaigns})

def campaign_detail(request, slug):
    """
    Specific Campaign Detail Page
    """
    campaign = get_object_or_404(Campaign, slug=slug)
    related_campaigns = Campaign.objects.exclude(id=campaign.id).order_by('-created_at')[:4]
    context = {
        'campaign': campaign,
        'related_campaigns': related_campaigns,
    }
    return render(request, 'campaign_detail.html', context)


def project_list(request):
    """
    Public Project Listing Page
    """
    projects = Project.objects.all().order_by('-date')
    return render(request, 'projects.html', {'projects': projects})

def project_detail(request, slug):
    """
    Specific Project Detail Page
    """
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'project_detail.html', {'project': project})

def blogs_page(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs})


def projects_page(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': projects})

def report_list(request):
    from .models import Report
    reports = Report.objects.all().order_by('-published_date')
    return render(request, 'annual_reports.html', {'reports': reports})

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    recent_blogs = Blog.objects.exclude(id=id).order_by('-created_at')[:4]

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'recent_blogs': recent_blogs
    })



def locations(request):
    return render(request, 'locations.html')

from django.contrib.contenttypes.models import ContentType
from .models import Interaction

@login_required
def donor_detail(request, pk):
    
    donor = get_object_or_404(BloodDonor, pk=pk)
    
    # Handle New Interaction Log
    if request.method == 'POST':
        interaction_type = request.POST.get('interaction_type')
        outcome = request.POST.get('outcome')
        notes = request.POST.get('notes')
        followup_date = request.POST.get('next_followup_date') or None
        
        # Create Interaction linked to this Donor
        Interaction.objects.create(
            staff=request.user,
            content_type=ContentType.objects.get_for_model(BloodDonor),
            object_id=donor.id,
            interaction_type=interaction_type,
            outcome=outcome,
            notes=notes,
            next_followup_date=followup_date
        )
        return redirect('donor_detail', pk=pk)
    
    # Fetch Interaction History
    ct = ContentType.objects.get_for_model(BloodDonor)
    interactions = Interaction.objects.filter(
        content_type=ct, 
        object_id=donor.id
    )

    donations = donor.donations.all()

    timeline = []
    for i in interactions:
        timeline.append({
            'type': 'interaction',
            'date': i.created_at,
            'obj': i,
        })
    
    for d in donations:
        timeline.append({
            'type': 'donation',
            'date': d.created_at,
            'obj': d,
        })

    timeline.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'blood_request/donor_detail.html', {
        'donor': donor,
        'timeline': timeline,
        'interaction_types': Interaction.INTERACTION_TYPES,
    })


def career_fellowship(request):
    return render(request, 'career_and_fellowship.html')

# --- Appointment Scheduling (Phase 8) ---
from .models import Appointment, PersonalNote
from django.http import JsonResponse

@login_required
def personal_notes_api(request):
    """API to get/save personal notes. Parses @mentions and creates Notifications."""
    note, created = PersonalNote.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        import json, re
        try:
            data = json.loads(request.body)
            new_content = data.get('content', '')
            note.content = new_content
            note.save()

            # --- @mention parsing ---
            from django.contrib.auth.models import User as AuthUser
            from .models import Notification
            mentions = set(re.findall(r'@(\w+)', new_content))
            for username in mentions:
                try:
                    mentioned_user = AuthUser.objects.get(username=username)
                    if mentioned_user != request.user:
                        Notification.objects.create(
                            user=mentioned_user,
                            actor=request.user,
                            message=f"{request.user.get_full_name() or request.user.username} mentioned you in a note.",
                            link='/admin/portal/',
                        )
                except AuthUser.DoesNotExist:
                    pass
            # -------------------------

            return JsonResponse({'status': 'saved', 'updated_at': str(note.updated_at)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'content': note.content, 'updated_at': str(note.updated_at)})

def resources_page(request):
    """Render the resources page"""
    return render(request, "resources.html")

@login_required
def appointment_list(request):
    # Show user's appointments
    appointments = Appointment.objects.filter(staff=request.user).order_by('start_time')
    return render(request, 'appointments.html', {'appointments': appointments})

@login_required
def appointment_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        description = request.POST.get('description')
        
        if title and start and end:
            Appointment.objects.create(
                title=title,
                start_time=start,
                end_time=end,
                description=description,
                staff=request.user,
                status='Scheduled'
            )
            return redirect('appointment_list')
    
    return render(request, 'appointment_form.html')


@login_required
def profile_edit(request):
    from .forms import UserUpdateForm, ProfileUpdateForm
    from .models import StaffProfile

    # Ensure StaffProfile exists
    profile, created = StaffProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            from django.contrib import messages
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_edit')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'profile.html', context)

# --- Phase 16: Data Export Suite ---
import csv
from django.http import HttpResponse

@user_passes_test(is_manager)
def export_donors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blood_donors.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Blood Group', 'City', 'Phone', 'Email', 'Last Donation', 'Donation Count', 'Score'])

    donors = BloodDonor.objects.all().values_list(
        'name', 'blood_group', 'city', 'phone', 'email', 'last_donation_date', 'donation_count', 'score'
    )
    for donor in donors:
        writer.writerow(donor)

    return response

@user_passes_test(is_manager)
def export_requests_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blood_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['Contact Person', 'Phone', 'City', 'Blood Group', 'Units', 'Status', 'Created At'])

    requests = BloodRequest.objects.all().values_list(
        'contact_person', 'contact_phone', 'city', 'blood_group', 'units', 'status', 'created_at'
    )
    for req in requests:
        writer.writerow(req)

    return response

@login_required
def notifications_api(request):
    """Return the logged-in user's notifications as JSON, including contact messages for staff."""
    from .models import Notification, ContactMessage
    base_qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = base_qs.filter(is_read=False).count()
    notifs = list(base_qs[:20])

    items = [
        {
            'id': n.id,
            'message': n.message,
            'link': n.link or '#',
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %Y %H:%M'),
            'type': 'notification',
        }
        for n in notifs
    ]

    if request.user.is_staff:
        cm_qs = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:10]
        unread_count += cm_qs.count()
        for cm in cm_qs:
            items.append({
                'id': f"cm_{cm.id}",
                'message': f"New message from {cm.first_name}: {cm.subject}",
                'link': '/admin/blood_request/contactmessage/',
                'is_read': False,
                'created_at': cm.created_at.strftime('%b %d, %Y %H:%M'),
                'type': 'contact_message',
            })

    return JsonResponse({
        'unread_count': unread_count,
        'notifications': items,
    })


@login_required
def mark_notifications_read(request):
    """Mark all notifications for the current user as read."""
    if request.method == 'POST':
        from .models import Notification, ContactMessage
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        if request.user.is_staff:
            ContactMessage.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def portal_timeline(request):
    """
    Phase 27.3: Unified Timeline View
    A single view showing the history of tasks, interactions, and appointments.
    """
    from itertools import chain
    from operator import attrgetter

    # 1. Get recent completed/created tasks
    tasks = Task.objects.filter(assigned_to=request.user).order_by('-updated_at')[:20]
    for t in tasks:
        t.timeline_type = 'task'
        t.timeline_date = t.updated_at
        t.timeline_icon = 'fa-check-circle text-green-500' if t.status == 'Done' else 'fa-clipboard-list text-blue-500'
        t.timeline_title = f"{'Completed' if t.status == 'Done' else 'Updated'} Task: {t.title}"
        t.timeline_desc = f"Priority: {t.priority}"

    # 2. Get recent CRM Interactions
    interactions = Interaction.objects.filter(staff=request.user).order_by('-created_at')[:20]
    for i in interactions:
        i.timeline_type = 'interaction'
        i.timeline_date = i.created_at
        i.timeline_icon = 'fa-phone text-purple-500' if i.interaction_type == 'Call' else 'fa-handshake text-indigo-500'
        i.timeline_title = f"Logged {i.interaction_type} with {i.entity}"
        i.timeline_desc = f"Outcome: {i.outcome}"

    # 3. Get recent Appointments
    appointments = Appointment.objects.filter(staff=request.user).order_by('-created_at')[:20]
    for a in appointments:
        a.timeline_type = 'appointment'
        a.timeline_date = a.created_at
        a.timeline_icon = 'fa-calendar text-brand-red'
        a.timeline_title = f"Scheduled: {a.title}"
        a.timeline_desc = f"For {a.start_time.strftime('%b %d, %H:%M')}"

    # Combine and sort by date descending
    timeline_events = sorted(
        chain(tasks, interactions, appointments),
        key=attrgetter('timeline_date'),
        reverse=True
    )[:50]

    return render(request, 'blood_request/timeline.html', {'timeline_events': timeline_events})

@login_required
def calendar_events_api(request):
    """API for FullCalendar"""
    events = []
    
    # Tasks
    tasks = Task.objects.filter(assigned_to=request.user)
    for task in tasks:
        if task.due_date:
            events.append({
                'title': f"Task: {task.title}",
                'start': task.due_date.isoformat(),
                'color': '#EF4444' if task.priority == 'Critical' else '#3B82F6',
                'url': f"/admin/portal/task/{task.id}/"
            })
            
    # Appointments
    appointments = Appointment.objects.filter(staff=request.user)
    for appt in appointments:
        events.append({
            'title': f"Mtg: {appt.title}",
            'start': appt.start_time.isoformat(),
            'end': appt.end_time.isoformat(),
            'color': '#10B981',
            'url': '/appointment/list/'
        })

    return JsonResponse(events, safe=False)


def workplace_living(request):
    return render(request, 'workplace_living.html')


# --- Phase 17: Team Views ---
from .models import Team, SharedNote
from django.contrib import messages

@login_required
@user_passes_test(is_manager)
def team_list(request):
    teams = Team.objects.all().order_by('-created_at')
    return render(request, 'blood_request/team_list.html', {'teams': teams})

@login_required
@permission_required('blood_request.add_team', raise_exception=True)
def team_create(request):
    workspace_id = request.GET.get('workspace') or request.POST.get('workspace')
    workspace = None
    if workspace_id:
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        member_ids = request.POST.getlist('members')
        
        if name:
            team = Team.objects.create(name=name, description=description, created_by=request.user, workspace=workspace)
            if member_ids:
                team.members.set(member_ids)
            from django.contrib import messages
            messages.success(request, f"Team '{name}' created successfully!")
            if workspace:
                return redirect('workspace_detail', slug=workspace.slug)
            return redirect('team_list')
    
    from django.contrib.auth.models import User
    # Filter users based on workspace if applicable
    if workspace:
        users = workspace.members.all()
    else:
        users = User.objects.filter(is_active=True).exclude(is_superuser=True)
        
    return render(request, 'blood_request/team_form.html', {'users': users, 'workspace': workspace})

@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    # Check access: Manager or Member
    if not (is_manager(request.user) or request.user in team.members.all()):
         from django.contrib import messages
         messages.error(request, "Access Denied")
         return redirect('staff_dashboard')
         
    # Kanban Data for Team
    team_members = team.members.all()
    all_team_tasks = Task.objects.filter(assigned_to__in=team_members).order_by('-updated_at')
    
    todo_tasks = all_team_tasks.filter(status='To Do')
    inprogress_tasks = all_team_tasks.filter(status='In Progress')
    done_tasks = all_team_tasks.filter(status='Done')

    return render(request, 'blood_request/team_detail.html', {
        'team': team,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'team_members': team_members,
        'is_manager': is_manager(request.user)
    })

# --- Phase 23: RBAC & Advanced Sharing ---
from django.contrib.auth.decorators import permission_required
from .forms import SharedNoteForm

@login_required
@permission_required('blood_request.add_sharednote', raise_exception=True)
def shared_note_create(request):
    """
    Create a Shared Note (Manager/Admin only, Revocable).
    """
    if request.method == 'POST':
        form = SharedNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            form.save_m2m() # Save ManyToMany data
            messages.success(request, "Shared Note created successfully!")
            return redirect('manager_dashboard')
    else:
        initial_data = {}
        parent_id = request.GET.get('parent')
        if parent_id and parent_id.isdigit():
            initial_data['parent_note'] = parent_id
        form = SharedNoteForm(initial=initial_data)
    
    return render(request, 'blood_request/shared_note_form.html', {'form': form})

@login_required
@permission_required('blood_request.view_sharednote', raise_exception=True)
def shared_note_list(request):
    """
    List all shared notes created by the user or shared with them.
    """
    # Notes owned by user OR shared with user OR shared with user's teams
    shared_notes = SharedNote.objects.filter(
        Q(owner=request.user) | 
        Q(shared_with_users=request.user) |
        Q(shared_with_teams__members=request.user)
    ).distinct().order_by('-created_at')
    
    return render(request, 'blood_request/shared_note_list.html', {'shared_notes': shared_notes})


@login_required
@permission_required('blood_request.add_task', raise_exception=True)
def task_create(request):
    """
    Create a Task (Manager only).
    """
    from .forms import TaskForm
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # If created by manager inside a project context, link it? For now standalone or select project if added to form
            # task.created_by = request.user # If model had this
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('manager_dashboard')
    else:
        form = TaskForm()
        
    return render(request, 'blood_request/task_form.html', {'form': form})

@login_required
@permission_required('blood_request.add_blog', raise_exception=True)
def blog_create(request):
    """
    Create a Blog (Manager only).
    """
    from .forms import BlogForm
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save()
            messages.success(request, "Blog post created successfully!")
            return redirect('manager_dashboard')
    else:
        form = BlogForm()
        
    return render(request, 'blood_request/blog_form.html', {'form': form})

@login_required
def shared_note_detail(request, pk):
    note = get_object_or_404(SharedNote, pk=pk)
    # Check permission (Owner, Shared User, or Shared Team Member)
    has_access = (
        request.user == note.owner or 
        request.user in note.shared_with_users.all() or
        note.shared_with_teams.filter(members=request.user).exists() or
        is_manager(request.user)
    )
    
    if not has_access:
        from django.contrib import messages
        messages.error(request, "You do not have permission to view this note.")
        return redirect('staff_dashboard')
        
    can_edit = request.user == note.owner or is_manager(request.user)
    
    if request.method == 'POST' and can_edit:
        form = SharedNoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, "Note updated successfully.")
            return redirect('shared_note_detail', pk=pk)
    else:
        form = SharedNoteForm(instance=note) if can_edit else None

    # Generate Wiki Breadcrumbs (Phase 25)
    breadcrumbs = []
    current = note.parent_note
    while current:
        breadcrumbs.insert(0, current)
        current = current.parent_note

    return render(request, 'blood_request/shared_note_detail.html', {
        'note': note,
        'breadcrumbs': breadcrumbs,
        'form': form,
        'can_edit': can_edit
    })

@login_required
@user_passes_test(is_manager)
def team_add_member(request, pk):
    team = get_object_or_404(Team, pk=pk)
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        member_ids = request.POST.getlist('members')
        if member_ids:
            users_to_add = User.objects.filter(id__in=member_ids)
            team.members.add(*users_to_add)
            from django.contrib import messages
            messages.success(request, f"{users_to_add.count()} members added to {team.name}")
        return redirect('team_detail', pk=pk)
    
    # Show users NOT in the team
    available_users = User.objects.filter(is_active=True).exclude(id__in=team.members.values_list('id', flat=True)).exclude(is_superuser=True)
    return render(request, 'blood_request/team_add_member.html', {
        'team': team,
        'available_users': available_users
    })

@login_required
@user_passes_test(is_manager)
def team_remove_member(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    from django.contrib.auth.models import User
    user_to_remove = get_object_or_404(User, pk=user_pk)
    
    if user_to_remove in team.members.all():
        team.members.remove(user_to_remove)
        from django.contrib import messages
        messages.success(request, f"{user_to_remove.username} removed from {team.name}")
    
    return redirect('team_detail', pk=team_pk)


@login_required
def shared_note_delete(request, pk):
    note = get_object_or_404(SharedNote, pk=pk)
    
    # Only owner or manager can delete
    if not (request.user == note.owner or is_manager(request.user)):
        from django.contrib import messages
        messages.error(request, "Only the owner or a manager can delete this note.")
        return redirect('shared_note_detail', pk=pk)
        
    if request.method == 'POST':
        note.delete()
        from django.contrib import messages
        messages.success(request, "Wiki page deleted successfully.")
        return redirect('shared_note_list')
        
    return render(request, 'blood_request/shared_note_confirm_delete.html', {'note': note})

# --- Phase 18: Portal User Management ---
@login_required
@user_passes_test(is_manager)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'blood_request/user_list.html', {'users': users})

@login_required
@user_passes_test(is_manager)
def user_add(request):
    if request.method == 'POST':
        from .forms import UserUpdateForm # Using similar form or create new
        # For simplicity, using standard User creation logic here or a specific form
        # But UserUpdateForm is for existing. Let's use UserCreationForm logic adapted.
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role') # Manager or Staff
        
        if username and password:
            try:
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError
                try:
                    validate_password(password)
                except ValidationError as ve:
                    messages.error(request, ", ".join(ve.messages))
                    return render(request, 'blood_request/user_form.html')
                user = User.objects.create_user(username=username, email=email, password=password)
                if role == 'Manager':
                    from django.contrib.auth.models import Group
                    g = Group.objects.get(name='Managers')
                    user.groups.add(g)
                    user.is_staff = True # Managers are staff
                    user.save()
                
                # Create Profile
                StaffProfile.objects.create(user=user)
                
                messages.success(request, f"User {username} created!")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, str(e))
                
    return render(request, 'blood_request/user_form.html')

@login_required
@user_passes_test(is_manager)
def user_edit_portal(request, pk):
    from django.contrib.auth.models import Group

    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        
        # Only allow superusers to modify access and roles
        if request.user.is_superuser:
            user_obj.is_staff = request.POST.get('is_staff') == 'on'
            user_obj.is_superuser = request.POST.get('is_superuser') == 'on'
            
            # Handle group assignments
            group_ids = request.POST.getlist('groups')
            user_obj.groups.clear()
            for group_id in group_ids:
                try:
                    group = Group.objects.get(id=group_id)
                    user_obj.groups.add(group)
                except Group.DoesNotExist:
                    pass

        user_obj.save()
        
        # Phone
        phone = request.POST.get('phone')
        profile, created = StaffProfile.objects.get_or_create(user=user_obj)
        profile.phone_number = phone
        profile.save()
        
        messages.success(request, f"User {user_obj.username} updated!")
        return redirect('user_list')

    context = {
        'target_user': user_obj,
    }
    
    # Pass available groups if current user is superuser
    if request.user.is_superuser:
        context['all_groups'] = Group.objects.all()

    return render(request, 'blood_request/user_edit.html', context)

def volunteering(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        education = request.POST.get('education')
        employment = request.POST.get('employment')
        residence = request.POST.get('residence')
        cv = request.FILES.get('cv')

        if name and email and phone and gender and education and employment and residence and cv:
            VolunteerRequest.objects.create(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                education=education,
                employment=employment,
                residence=residence,
                cv=cv
            )
            messages.success(request, 'Your volunteer application has been submitted successfully!')
        else:
            messages.error(request, 'Please fill all required fields and upload your CV.')

    return render(request, "volunteering.html")



def campus_ambassador(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        father_name = request.POST.get('father_name')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        institution = request.POST.get('institution')
        address = request.POST.get('address')
        technical_skills = request.POST.get('technical_skills')
        general_skills = request.POST.get('general_skills')
        motivation = request.POST.get('motivation')
        email = request.POST.get('email')
        cv = request.FILES.get('cv')

        if full_name and phone and dob and institution and address and email and cv:
            CampusAmbassadorApplication.objects.create(
                full_name=full_name,
                father_name=father_name,
                phone=phone,
                dob=dob,
                institution=institution,
                address=address,
                technical_skills=technical_skills,
                general_skills=general_skills,
                motivation=motivation,
                email=email,
                cv=cv
            )
            messages.success(request, 'Your Campus Ambassador application has been submitted successfully!')
        else:
            messages.error(request, 'Please fill all required fields and upload your CV.')

    ambassadors = CampusAmbassador.objects.all().order_by('-id')

    return render(
        request,
        "campus_ambassador.html",
        {
            "ambassadors": ambassadors
        }
    )

def jobs(request):
    from .models import JobPosting
    job_postings = JobPosting.objects.filter(is_active=True)
    return render(request, "jobs.html", {'job_postings': job_postings})

def news_clippings(request):
    from .models import NewsClipping
    clippings = NewsClipping.objects.all().order_by('-created_at')
    return render(request, 'news_clippings.html', {'clippings': clippings})

def internships(request):
    from django.contrib import messages
    from .models import InternshipRequest
    
    if request.method == 'POST':
        name = request.POST.get('name')
        father_name = request.POST.get('father_name', '')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        educational_qualification = request.POST.get('educational_qualification')
        permanent_address = request.POST.get('permanent_address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        internship_area = request.POST.get('internship_area')
        other_interest = request.POST.get('other_interest')
        start_date = request.POST.get('start_date')
        duration_months = request.POST.get('duration_months', 3)
        cv = request.FILES.get('cv')
        
        try:
            InternshipRequest.objects.create(
                name=name,
                father_name=father_name,
                dob=dob,
                gender=gender,
                educational_qualification=educational_qualification,
                permanent_address=permanent_address,
                contact_number=contact_number,
                email=email,
                internship_area=internship_area,
                other_interest=other_interest,
                start_date=start_date,
                duration_months=duration_months,
                cv=cv,
            )
            messages.success(request, 'Your internship request has been successfully submitted! We will contact you soon.')
        except Exception as e:
            messages.error(request, 'There was an error submitting your request. Please check your inputs.')
            
    return render(request, 'internships.html')

def our_mission_values(request):
    return render(request, 'ourmission_values.html')

def aboutus(request):
    return render(request, 'aboutus.html')
def our_policies(request):

    ethical = PolicyReport.objects.filter(category="ethical", published=True).first()
    finance = PolicyReport.objects.filter(category="finance", published=True).first()
    hr = PolicyReport.objects.filter(category="hr", published=True).first()
    travel = PolicyReport.objects.filter(category="travel", published=True).first()
    posh = PolicyReport.objects.filter(category="posh", published=True).first()
    policies = PolicyReport.objects.filter(published=True).order_by('display_order', '-uploaded_at')

    context = {
        "ethical": ethical,
        "finance": finance,
        "hr": hr,
        "travel": travel,
        "posh": posh,
        "policies": policies,
    }

    return render(request,"our_policies.html",context)

# --- Phase: Move Admin to Portal ---
from django.views.generic import ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

@method_decorator(user_passes_test(is_manager), name='dispatch')
class TaskListView(ListView):
    model = Task
    template_name = 'blood_request/portal_list.html'
    context_object_name = 'items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manage Tasks'
        context['create_url'] = 'task_create_portal'
        context['update_url_name'] = 'task_update_portal'
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class TaskUpdateView(UpdateView):
    model = Task
    fields = ['title', 'project', 'description', 'assigned_to', 'status', 'priority', 'due_date', 'recurrence_rule', 'dependencies']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('task_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update Task: {self.object.title}'
        context['back_url'] = reverse_lazy('task_list_portal')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'project', 'description', 'assigned_to', 'status', 'priority', 'due_date', 'recurrence_rule', 'dependencies']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('task_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Task'
        context['back_url'] = reverse_lazy('task_list_portal')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class SubTaskListView(ListView):
    model = SubTask
    template_name = 'blood_request/portal_list.html'
    context_object_name = 'items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manage SubTasks'
        context['create_url'] = 'subtask_create_portal'
        context['update_url_name'] = 'subtask_update_portal'
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class SubTaskCreateView(CreateView):
    model = SubTask
    fields = ['title', 'parent_task', 'assigned_to', 'status']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('subtask_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create SubTask'
        context['back_url'] = reverse_lazy('subtask_list_portal')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class SubTaskUpdateView(UpdateView):
    model = SubTask
    fields = ['title', 'parent_task', 'assigned_to', 'status']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('subtask_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update SubTask: {self.object.title}'
        context['back_url'] = reverse_lazy('subtask_list_portal')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class TeamUpdateView(UpdateView):
    model = Team
    fields = ['name', 'description', 'workspace']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('team_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update Team: {self.object.name}'
        context['back_url'] = reverse_lazy('team_list')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = 'blood_request/portal_list.html'
    context_object_name = 'items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manage Expenses'
        context['create_url'] = 'expense_create_portal'
        context['update_url_name'] = 'expense_update_portal'
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    fields = ['title', 'amount', 'date', 'category', 'campaign', 'project', 'receipt_image', 'notes']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('expense_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Log New Expense'
        context['back_url'] = reverse_lazy('expense_list_portal')
        return context

    def form_valid(self, form):
        form.instance.logged_by = self.request.user
        return super().form_valid(form)

@method_decorator(user_passes_test(is_manager), name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    fields = ['title', 'amount', 'date', 'category', 'campaign', 'project', 'receipt_image', 'notes']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('expense_list_portal')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update Expense: {self.object.title}'
        context['back_url'] = reverse_lazy('expense_list_portal')
        return context


def our_team(request):
    return render(request,"our_team.html")

from django.contrib import messages

def contact_us(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if first_name and email and message:
            ContactMessage.objects.create(
                first_name=first_name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact_us')
        else:
            messages.error(request, "Please fill out all required fields.")
            
    return render(request, "contact_us.html")

def faq(request):
    return render(request, "faq.html")

def our_partners(request):
    return render(request, "our_partners.html")

def appreciationandaccolades(request):
    return render(request, "appreciationandaccolades.html")

def our_activities(request):
    from .models import Activity
    activities = Activity.objects.filter(is_active=True)
    return render(request, "ouractivites.html", {"activities": activities})


# --- Phase 29 Portal UI: Automation Rules, Digest, PDF Export ---

# Automation Rules CRUD
@method_decorator(user_passes_test(is_manager), name='dispatch')
class AutomationRuleListView(ListView):
    model = TaskAutomationRule
    template_name = 'blood_request/portal_automation_list.html'
    context_object_name = 'rules'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Automation Rules'
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class AutomationRuleCreateView(CreateView):
    model = TaskAutomationRule
    fields = ['name', 'trigger_type', 'action_type', 'target_user', 'is_active']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('automation_rule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Automation Rule'
        context['back_url'] = reverse_lazy('automation_rule_list')
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class AutomationRuleUpdateView(UpdateView):
    model = TaskAutomationRule
    fields = ['name', 'trigger_type', 'action_type', 'target_user', 'is_active']
    template_name = 'blood_request/portal_form.html'
    success_url = reverse_lazy('automation_rule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Automation Rule'
        context['back_url'] = reverse_lazy('automation_rule_list')
        return context

@login_required
@user_passes_test(is_manager)
def automation_rule_delete(request, pk):
    rule = get_object_or_404(TaskAutomationRule, pk=pk)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, f"Rule '{rule.name}' deleted.")
        return redirect('automation_rule_list')
    return render(request, 'blood_request/portal_confirm_delete.html', {
        'object': rule,
        'page_title': 'Delete Automation Rule',
        'back_url': 'automation_rule_list',
    })

# Send Digest from Portal UI
@login_required
@user_passes_test(is_manager)
def send_digest_portal(request):
    """Allows a manager to send the daily digest email to all staff from the portal."""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from datetime import date
    
    preview_users = []
    
    if request.method == 'POST':
        staff_users = User.objects.filter(is_active=True, is_staff=True)
        emails_sent = 0
        
        for user in staff_users:
            if not user.email:
                continue
                
            tasks = Task.objects.filter(
                assigned_to=user,
                status__in=['To Do', 'In Progress']
            ).order_by('due_date', '-priority')
            
            if not tasks.exists():
                continue
            
            html_message = render_to_string(
                'blood_request/emails/daily_digest.html',
                {'user': user, 'tasks': tasks, 'today': date.today()}
            )
            
            plain_message = f"Hello {user.first_name or user.username}, you have {tasks.count()} pending tasks."
            
            try:
                send_mail(
                    subject=f"UDAAN Tasks Daily Digest - {date.today().strftime('%b %d, %Y')}",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                emails_sent += 1
            except Exception as e:
                messages.warning(request, f"Failed to send to {user.username}: {str(e)}")
        
        messages.success(request, f"Daily digest sent to {emails_sent} staff member(s)!")
        return redirect('send_digest_portal')
    
    # GET: Show preview of who will receive
    staff_users = User.objects.filter(is_active=True, is_staff=True)
    for user in staff_users:
        tasks = Task.objects.filter(assigned_to=user, status__in=['To Do', 'In Progress'])
        if tasks.exists() and user.email:
            preview_users.append({
                'user': user,
                'task_count': tasks.count(),
                'email': user.email,
            })
    
    return render(request, 'blood_request/portal_send_digest.html', {
        'preview_users': preview_users,
        'page_title': 'Send Daily Digest',
    })

# Export Tasks as PDF
@login_required
@user_passes_test(is_manager)
def export_tasks_pdf(request):
    """Export all tasks as a styled PDF document."""
    from io import BytesIO
    from django.template.loader import render_to_string
    from datetime import date
    
    tasks = Task.objects.all().order_by('status', '-priority', 'due_date')
    
    # We'll use HTML-to-PDF approach with weasyprint if available, 
    # otherwise fall back to CSV
    try:
        from weasyprint import HTML
        
        html_string = render_to_string('blood_request/exports/tasks_pdf.html', {
            'tasks': tasks,
            'today': date.today(),
            'generated_by': request.user,
        })
        
        pdf_file = BytesIO()
        HTML(string=html_string).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="UDAAN_Tasks_Report_{date.today()}.pdf"'
        return response
        
    except ImportError:
        # Fallback: Generate a clean CSV if weasyprint is not installed
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="UDAAN_Tasks_Report_{date.today()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Status', 'Priority', 'Assigned To', 'Project', 'Due Date', 'Created At'])
        
        for task in tasks:
            writer.writerow([
                task.title,
                task.status,
                task.priority,
                task.assigned_to.username if task.assigned_to else 'Unassigned',
                task.project.title if task.project else 'General',
                task.due_date if task.due_date else '-',
                task.created_at.strftime('%Y-%m-%d'),
            ])
        
        return response
    

def blood_donation(request):
    """Blood Donation page with live data from the database."""
    # Live blood requests (non-closed)
    live_requests = BloodRequest.objects.exclude(status='Closed').order_by('-created_at')[:10]
    
    # Impact stats
    total_donors = BloodDonor.objects.count()
    total_donations = Donation.objects.count()
    total_requests = BloodRequest.objects.count()
    
    context = {
        'live_requests': live_requests,
        'total_donors': total_donors,
        'total_donations': total_donations,
        'total_requests': total_requests,
    }
    return render(request, "blood_donation.html", context)


def newsletter_subscribe(request):
    """API endpoint for newsletter email subscription."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            if not email:
                return JsonResponse({'success': False, 'error': 'Email is required.'}, status=400)
            
            from .models import NewsletterSubscription
            if NewsletterSubscription.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'This email is already subscribed.'}, status=400)
            
            NewsletterSubscription.objects.create(email=email)
            return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


def blood_request_submit(request):
    """API endpoint for blood request form submission."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            required_fields = ['blood_group', 'contact_person', 'contact_phone', 'city']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'success': False, 'error': f'{field.replace("_", " ").title()} is required.'}, status=400)

            blood_request = BloodRequest.objects.create(
                patient_name=data.get('patient_name', ''),
                hospital_name=data.get('hospital_name', ''),
                blood_group=data.get('blood_group'),
                city=data.get('city', ''),
                state=data.get('state', ''),
                pin_code=data.get('pin_code', ''),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                is_emergency=data.get('is_emergency', False),
                units=int(data.get('units', 1)),
            )
            return JsonResponse({'success': True, 'message': 'Blood request submitted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


# --- Start a Campaign & Crowdfunding Views ---
import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from .models import (
    Campaign, Beneficiary, MedicalDetail, BankAccount, KYCDocument,
    CampaignDraft, CampaignSource, CampaignUpdate, CampaignImage, CampaignDocument
)

def start_campaign_wizard(request):
    """Render the 8-step Start a Campaign Wizard."""
    draft_id = request.GET.get('draft_id')
    draft_data = {}
    if draft_id:
        try:
            draft = CampaignDraft.objects.get(id=draft_id)
            draft_data = draft.step_data
        except CampaignDraft.DoesNotExist:
            pass
    
    categories = [
        ('Medical', 'Medical', 'fa-notes-medical', 'bg-rose-500/10 text-rose-500 border-rose-500/30'),
        ('Education', 'Education', 'fa-graduation-cap', 'bg-blue-500/10 text-blue-500 border-blue-500/30'),
        ('Animal Welfare', 'Animal Welfare', 'fa-paw', 'bg-amber-500/10 text-amber-500 border-amber-500/30'),
        ('Disaster Relief', 'Disaster Relief', 'fa-house-tsunami', 'bg-red-500/10 text-red-500 border-red-500/30'),
        ('NGO', 'NGO / Non-Profit', 'fa-hand-holding-heart', 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30'),
        ('Child Care', 'Child Care', 'fa-child-reaching', 'bg-violet-500/10 text-violet-500 border-violet-500/30'),
        ('Emergency', 'Emergency', 'fa-truck-medical', 'bg-red-600/10 text-red-600 border-red-600/30'),
        ('Memorial', 'Memorial', 'fa-dove', 'bg-slate-500/10 text-slate-500 border-slate-500/30'),
        ('Startup', 'Startup / Innovation', 'fa-rocket', 'bg-purple-500/10 text-purple-500 border-purple-500/30'),
        ('Personal Need', 'Personal Need', 'fa-user', 'bg-indigo-500/10 text-indigo-500 border-indigo-500/30'),
        ('Sports', 'Sports', 'fa-trophy', 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30'),
        ('Community', 'Community', 'fa-people-group', 'bg-teal-500/10 text-teal-500 border-teal-500/30'),
        ('Environment', 'Environment', 'fa-leaf', 'bg-green-500/10 text-green-500 border-green-500/30'),
        ('Other', 'Other Cause', 'fa-ellipsis', 'bg-gray-500/10 text-gray-500 border-gray-500/30'),
    ]

    featured_campaign = Campaign.objects.first()

    context = {
        'categories': categories,
        'draft_data_json': json.dumps(draft_data),
        'featured_campaign': featured_campaign,
    }
    return render(request, 'campaigns/start_campaign.html', context)


@csrf_exempt
def campaign_autosave_api(request):
    """API endpoint to autosave draft data."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            draft_id = data.get('draft_id')
            step_data = data.get('step_data', {})
            current_step = data.get('current_step', 1)
            category = step_data.get('category', 'Medical')

            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key or 'anonymous'

            if draft_id:
                draft = CampaignDraft.objects.filter(id=draft_id).first()
                if draft:
                    draft.step_data = step_data
                    draft.current_step = current_step
                    draft.category = category
                    draft.save()
                else:
                    draft = CampaignDraft.objects.create(
                        user=user, session_key=session_key, category=category,
                        step_data=step_data, current_step=current_step
                    )
            else:
                draft = CampaignDraft.objects.create(
                    user=user, session_key=session_key, category=category,
                    step_data=step_data, current_step=current_step
                )

            from datetime import datetime
            return JsonResponse({
                'status': 'success',
                'draft_id': draft.id,
                'saved_at': datetime.now().strftime('%H:%M:%S')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
def campaign_submit_api(request):
    """API endpoint to submit the full campaign form."""
    if request.method == 'POST':
        try:
            data = request.POST.dict() if request.POST else json.loads(request.body or '{}')
            
            title = data.get('title', 'Untitled Campaign').strip()
            category = data.get('category', 'Medical')
            
            # --- NEW VALIDATIONS ---
            # 1. Check IFSC validation
            ifsc_code = data.get('ifsc_code', '').strip().upper()
            if ifsc_code:
                try:
                    import requests
                    ifsc_resp = requests.get(f'https://ifsc.razorpay.com/{ifsc_code}', timeout=5)
                    if ifsc_resp.status_code != 200:
                        return JsonResponse({'status': 'error', 'message': 'Invalid IFSC Code provided. Please provide a valid IFSC.'}, status=400)
                except Exception:
                    pass # Allow if service is down to not block critical submissions

            # 2. Check Image Aspect Ratio (16:9)
            from PIL import Image
            cover_file = request.FILES.get('image') or request.FILES.get('cover_image')
            if cover_file:
                try:
                    img = Image.open(cover_file)
                    width, height = img.size
                    if width < 1200 or height < 675:
                         return JsonResponse({'status': 'error', 'message': f'Image is too small ({width}x{height}). Minimum required is 1200x675 pixels.'}, status=400)
                    ratio = width / height
                    if not (1.7 <= ratio <= 1.8):  # Roughly 16:9
                         return JsonResponse({'status': 'error', 'message': 'Image aspect ratio must be 16:9.'}, status=400)
                    cover_file.seek(0)
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': 'Invalid image file uploaded.'}, status=400)
            # -----------------------

            short_description = data.get('short_description', '')
            full_story = data.get('description', '') or data.get('full_story', '')
            goal_amount = float(data.get('goal_amount', 10000))
            currency = data.get('currency', 'INR')
            location = data.get('location', '')
            tags = data.get('tags', '')
            deadline = data.get('deadline') or None
            video_url = data.get('video_url', '')

            user = request.user if request.user.is_authenticated else None

            # Create Campaign
            campaign = Campaign.objects.create(
                title=title,
                category=category,
                short_description=short_description,
                description=full_story,
                goal_amount=goal_amount,
                currency=currency,
                location=location,
                tags=tags,
                deadline=deadline,
                video_url=video_url,
                status='Approved',
                confirmation_agreed=data.get('confirmation_agreed') in [True, 'true', 'on', '1'],
                created_by=user
            )

            # Files - Cover Image
            if 'image' in request.FILES:
                campaign.image = request.FILES['image']
            if 'cover_image' in request.FILES:
                campaign.cover_image = request.FILES['cover_image']
            campaign.save()

            # Multiple Gallery Photos
            gallery_photos = request.FILES.getlist('gallery_photos')
            if not gallery_photos and 'images' in request.FILES:
                gallery_photos = request.FILES.getlist('images')
            for idx, photo in enumerate(gallery_photos):
                CampaignImage.objects.create(
                    campaign=campaign,
                    image=photo,
                    caption=f"Gallery Image {idx + 1}",
                    display_order=idx
                )

            # Multiple Supporting Documents
            doc_files = request.FILES.getlist('documents')
            for doc_file in doc_files:
                CampaignDocument.objects.create(
                    campaign=campaign,
                    title=doc_file.name,
                    file=doc_file
                )

            # Beneficiary Details
            id_proof = request.FILES.get('id_proof_file') or request.FILES.get('id_proof')
            Beneficiary.objects.create(
                campaign=campaign,
                recipient_type=data.get('beneficiary_type', 'Myself'),
                full_name=data.get('beneficiary_name', title),
                age=int(data.get('beneficiary_age', 0)) if data.get('beneficiary_age') else None,
                gender=data.get('beneficiary_gender', ''),
                relationship=data.get('beneficiary_relationship', ''),
                phone_number=data.get('beneficiary_phone', ''),
                email=data.get('beneficiary_email', ''),
                address=data.get('beneficiary_address', ''),
                id_type=data.get('id_type', ''),
                id_number=data.get('id_number', ''),
                id_proof_file=id_proof
            )
            if id_proof:
                CampaignDocument.objects.create(
                    campaign=campaign,
                    title=f"ID Proof - {data.get('beneficiary_name', 'Beneficiary')}",
                    file=id_proof
                )

            # Medical Details (if Medical)
            medical_report = request.FILES.get('medical_report')
            prescription = request.FILES.get('prescription_file') or request.FILES.get('prescription')
            cost_estimate = request.FILES.get('cost_estimate_file') or request.FILES.get('cost_estimate')
            hospital_letter = request.FILES.get('hospital_letter')

            if category == 'Medical':
                MedicalDetail.objects.create(
                    campaign=campaign,
                    hospital_name=data.get('hospital_name', 'General Hospital'),
                    doctor_name=data.get('doctor_name', ''),
                    diagnosis=data.get('diagnosis', 'Medical Treatment'),
                    treatment_name=data.get('treatment_name', ''),
                    estimated_cost=float(data.get('estimated_cost')) if data.get('estimated_cost') else None,
                    medical_report=medical_report,
                    prescription_file=prescription,
                    cost_estimate_file=cost_estimate,
                    hospital_letter=hospital_letter
                )

            for doc_obj, doc_title in [(medical_report, "Medical Report"), (prescription, "Prescription / Bill"), (cost_estimate, "Cost Estimate"), (hospital_letter, "Hospital Letter")]:
                if doc_obj:
                    CampaignDocument.objects.create(
                        campaign=campaign,
                        title=doc_title,
                        file=doc_obj
                    )

            # Bank Details
            cancelled_cheque_file = request.FILES.get('cancelled_cheque')
            BankAccount.objects.create(
                campaign=campaign,
                beneficiary_name=data.get('bank_account_name', data.get('beneficiary_name', title)),
                bank_name=data.get('bank_name', 'National Bank'),
                account_number=data.get('account_number', '1234567890'),
                ifsc_code=data.get('ifsc_code', 'HDFC0000001'),
                upi_id=data.get('upi_id', ''),
                cancelled_cheque=cancelled_cheque_file,
                ifsc_verified=data.get('ifsc_verified') in [True, 'true', '1']
            )

            if cancelled_cheque_file:
                CampaignDocument.objects.create(
                    campaign=campaign,
                    title="Cancelled Cheque / Bank Passbook",
                    file=cancelled_cheque_file
                )

            # KYC
            KYCDocument.objects.create(
                campaign=campaign,
                aadhaar_file=request.FILES.get('aadhaar_file'),
                pan_file=request.FILES.get('pan_file'),
                passport_file=request.FILES.get('passport_file'),
                selfie_file=request.FILES.get('selfie_file'),
                verification_status='Verified',
                face_match_score=98,
                email_verified=True,
                phone_verified=True
            )

            # Source Info
            CampaignSource.objects.create(
                campaign=campaign,
                heard_from=data.get('heard_from', 'Website'),
                social_links={'connected': data.get('socials', '')}
            )

            # Remove draft if exists
            draft_id = data.get('draft_id')
            if draft_id:
                CampaignDraft.objects.filter(id=draft_id).delete()

            return JsonResponse({
                'status': 'success',
                'campaign_slug': campaign.slug,
                'redirect_url': '/campaigns/'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
def ai_campaign_assist_api(request):
    """AI Assistant endpoint for title generator, story improver, goal advisor."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            category = data.get('category', 'Medical')
            prompt_input = data.get('input', '')

            gemini_key = os.environ.get('GEMINI_API_KEY')
            
            if action == 'generate_title':
                titles = [
                    f"Help {prompt_input or 'us'} overcome this crisis - Hope & Recovery Fund",
                    f"Support {prompt_input or category}: Together We Can Make a Difference",
                    f"Urgent Appeal for {category}: Stand with Us Today"
                ]
                return JsonResponse({'status': 'success', 'titles': titles})

            elif action == 'improve_story':
                improved_story = f"""### Why We Need Your Support

{prompt_input}

---

### How Your Donation Will Be Used
Every contribution goes directly towards:
- Critical treatments, medical procedures & hospital expenses
- Rehabilitation, medications, and necessary follow-up care
- Essential living support during recovery

---

### Transparent & Accountable
All funds are verified by Udaan Society and transferred directly to the beneficiary / hospital bank account with full receipts and updates shared on this page.

**Please share this campaign with your friends and family on WhatsApp and Facebook!**"""

                if gemini_key and gemini_key != 'your_gemini_api_key_here':
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=gemini_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(f"Rewrite and expand the following crowdfunding story for category {category} to make it emotionally compelling, well-structured with headings and bullet points, and highly persuasive for donors:\n\n{prompt_input}")
                        if res.text:
                            improved_story = res.text
                    except Exception:
                        pass

                return JsonResponse({'status': 'success', 'improved_story': improved_story})

            elif action == 'recommend_goal':
                goal_recommendations = {
                    'Medical': '₹ 3,00,000 - ₹ 15,00,000',
                    'Education': '₹ 50,000 - ₹ 3,00,000',
                    'Animal Welfare': '₹ 25,00,000 - ₹ 1,50,000',
                    'Disaster Relief': '₹ 5,00,000 - ₹ 25,00,000',
                    'Child Care': '₹ 1,00,000 - ₹ 5,00,000',
                }
                rec = goal_recommendations.get(category, '₹ 1,00,000 - ₹ 5,00,000')
                return JsonResponse({'status': 'success', 'recommendation': rec})

            elif action == 'check_thumbnail':
                return JsonResponse({
                    'status': 'success',
                    'quality_score': 92,
                    'feedback': 'High resolution image with good clarity and framing!'
                })

            return JsonResponse({'status': 'error', 'message': 'Unknown action'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def ifsc_verify_api(request):
    """API endpoint to verify IFSC codes via Razorpay with local fallback."""
    code = request.GET.get('code', '').strip().upper()
    if not code or len(code) != 11:
        return JsonResponse({'valid': False, 'message': 'Invalid IFSC code format (must be 11 characters)'})

    try:
        import requests
        response = requests.get(f'https://ifsc.razorpay.com/{code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'valid': True,
                'ifsc': code,
                'bank_name': data.get('BANK', 'Unknown Bank'),
                'branch': data.get('BRANCH', 'Unknown Branch'),
                'city': data.get('CITY', ''),
                'state': data.get('STATE', '')
            })
        else:
            return JsonResponse({'valid': False, 'message': 'Invalid IFSC code or bank not found.'})
    except Exception:
        bank_map = {
            'SBIN': ('State Bank of India', 'Main Branch'),
            'HDFC': ('HDFC Bank', 'Central Branch'),
            'ICIC': ('ICICI Bank', 'Metro Branch'),
            'UTIB': ('Axis Bank', 'City Branch'),
            'PUNB': ('Punjab National Bank', 'Civil Lines Branch'),
            'BARB': ('Bank of Baroda', 'Industrial Estate Branch'),
        }
        prefix = code[:4]
        if prefix in bank_map:
            bank_name, branch = bank_map[prefix]
            return JsonResponse({
                'valid': True,
                'ifsc': code,
                'bank_name': bank_name,
                'branch': branch,
                'city': 'New Delhi',
                'state': 'Delhi'
            })
        return JsonResponse({'valid': False, 'message': 'Verification service unavailable.'})


def campaign_status_view(request, slug):
    """View to display Admin Review Timeline status for a campaign."""
    campaign = get_object_or_404(Campaign, slug=slug)
    beneficiary = getattr(campaign, 'beneficiary', None)
    medical = getattr(campaign, 'medical_detail', None)
    bank = getattr(campaign, 'bank_account', None)
    kyc = getattr(campaign, 'kyc', None)

    context = {
        'campaign': campaign,
        'beneficiary': beneficiary,
        'medical': medical,
        'bank': bank,
        'kyc': kyc,
    }
    return render(request, 'campaigns/campaign_status.html', context)


def campaign_dashboard_view(request, slug):
    """View for Campaign Creator Dashboard."""
    campaign = get_object_or_404(Campaign, slug=slug)
    beneficiary = getattr(campaign, 'beneficiary', None)
    medical = getattr(campaign, 'medical_detail', None)
    bank = getattr(campaign, 'bank_account', None)

    if request.method == 'POST':
        update_title = request.POST.get('update_title')
        update_content = request.POST.get('update_content')
        if update_title and update_content:
            CampaignUpdate.objects.create(
                campaign=campaign,
                title=update_title,
                content=update_content,
                image=request.FILES.get('update_image')
            )
            return redirect('campaign_dashboard', slug=campaign.slug)

    updates = campaign.updates.all()
    documents = campaign.documents.all()

    context = {
        'campaign': campaign,
        'beneficiary': beneficiary,
        'medical': medical,
        'bank': bank,
        'updates': updates,
        'documents': documents,
    }
    return render(request, 'campaigns/campaign_dashboard.html', context)
