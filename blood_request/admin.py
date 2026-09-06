from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django_ckeditor_5.widgets import CKEditor5Widget
from django.db import models

from django.utils.safestring import mark_safe

from .models import (
    PolicyReport, Report, Testimonial, StaffProfile, Announcement,
    Interaction, BloodDonor, Project, BloodRequest, Blog, BlogImage, Campaign,
    CampusAmbassador, CampusAmbassadorApplication, NewsClipping, ContactMessage,
    Activity, JobPosting, Donation, SubTask, TaskComment, Team, SharedNote,
    Workspace, WorkspaceMember, Expense, TaskAutomationRule, NewsletterSubscription, Task,
    InternshipRequest, VolunteerRequest, Beneficiary, MedicalDetail, BankAccount,
    KYCDocument, CampaignDraft, CampaignSource, CampaignUpdate, CampaignImage, CampaignDocument
)

class BeneficiaryInline(admin.StackedInline):
    model = Beneficiary
    extra = 0

class MedicalDetailInline(admin.StackedInline):
    model = MedicalDetail
    extra = 0

class BankAccountInline(admin.StackedInline):
    model = BankAccount
    extra = 0

class KYCDocumentInline(admin.StackedInline):
    model = KYCDocument
    extra = 0

class CampaignImageInline(admin.TabularInline):
    model = CampaignImage
    extra = 1
    fields = ('image',)

class CampaignDocumentInline(admin.TabularInline):
    model = CampaignDocument
    extra = 1
    fields = ('file',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'target_vs_raised', 'deadline', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'location', 'tags')
    inlines = [BeneficiaryInline, MedicalDetailInline, BankAccountInline, KYCDocumentInline, CampaignImageInline, CampaignDocumentInline]
    actions = ['approve_campaigns', 'verify_campaigns', 'reject_campaigns', 'request_docs_campaigns']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'short_description', 'description', 'location', 'tags', 'created_by')
        }),
        ('Media', {
            'fields': ('image', 'cover_image', 'video_url')
        }),
        ('Fundraising Target', {
            'fields': ('goal_amount', 'raised_amount', 'currency', 'deadline')
        }),
        ('Review & Status', {
            'fields': ('status', 'admin_feedback', 'confirmation_agreed')
        }),
    )

    @admin.action(description="Approve Selected Campaigns")
    def approve_campaigns(self, request, queryset):
        queryset.update(status='Approved', admin_feedback="Approved by Admin")

    @admin.action(description="Mark as Under Verification")
    def verify_campaigns(self, request, queryset):
        queryset.update(status='Under Verification')

    @admin.action(description="Reject Selected Campaigns")
    def reject_campaigns(self, request, queryset):
        queryset.update(status='Rejected')

    @admin.action(description="Request Additional Documents")
    def request_docs_campaigns(self, request, queryset):
        queryset.update(status='Need Documents')

    def target_vs_raised(self, obj):
        return f"{obj.currency} {obj.raised_amount} / {obj.goal_amount}"

@admin.register(CampaignDraft)
class CampaignDraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'current_step', 'updated_at')

@admin.register(CampaignUpdate)
class CampaignUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'created_at')

from .utils import generate_internship_offer_letter

# Custom branding for Django Administration
admin.site.site_header = "UDAAN Society Administration"
admin.site.site_title  = "UDAAN Admin Portal"
admin.site.index_title = "Welcome to the UDAAN Admin Panel"

from django import forms
from django.core.exceptions import ValidationError

class PolicyReportForm(forms.ModelForm):
    class Meta:
        model = PolicyReport
        fields = ('title', 'description', 'pdf_file', 'thumbnail', 'display_order', 'published')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter policy title'}),
            'description': forms.Textarea(attrs={'rows': 4, 'maxlength': 250, 'placeholder': 'Enter a short description of this policy.'}),
        }
        error_messages = {
            'title': {
                'required': "Policy title is required.",
            },
            'pdf_file': {
                'required': "Please upload a PDF document.",
            }
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            if not pdf_file.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
        return pdf_file

@admin.register(PolicyReport)
class PolicyReportAdmin(admin.ModelAdmin):
    form = PolicyReportForm
    list_display = ('title', 'published', 'updated_at', 'display_order')
    list_filter = ('published',)
    search_fields = ('title',)
    ordering = ('display_order', '-updated_at', '-uploaded_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description'),
            'description': 'This title will be displayed on the website.',
        }),
        ('Document Details', {
            'fields': ('pdf_file', 'thumbnail', 'display_order'),
        }),
        ('Publishing', {
            'fields': ('published',),
        }),
    )

    class Media:
        css = {
            'all': ('css/admin_policy_custom.css',)
        }

    def save_model(self, request, obj, form, change):
        if not obj.category:
            obj.category = 'ethical'
        super().save_model(request, obj, form, change)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'created_at')
    search_fields = ('title',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'is_active', 'created_at')
    list_filter = ('is_active',)

# Custom User Creation Form with Intern/Volunteer Import Option
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    intern_source = forms.ModelChoiceField(
        queryset=InternshipRequest.objects.all(),
        required=False,
        label="Import from Intern Application",
        help_text="Optional: Select an Intern to auto-populate details and assign to 'Interns' group."
    )
    volunteer_source = forms.ModelChoiceField(
        queryset=VolunteerRequest.objects.all(),
        required=False,
        label="Import from Volunteer Application",
        help_text="Optional: Select a Volunteer to auto-populate details and assign to 'Volunteers' group."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        intern = cleaned_data.get('intern_source')
        volunteer = cleaned_data.get('volunteer_source')

        if intern and volunteer:
            raise forms.ValidationError("Please select either an Intern or a Volunteer, not both.")

        if intern:
            if intern.email and not cleaned_data.get('email'):
                cleaned_data['email'] = intern.email
            if intern.name:
                parts = intern.name.split()
                if not cleaned_data.get('first_name'):
                    cleaned_data['first_name'] = parts[0]
                if not cleaned_data.get('last_name') and len(parts) > 1:
                    cleaned_data['last_name'] = ' '.join(parts[1:])
                if not cleaned_data.get('username'):
                    base_username = intern.email.split('@')[0].replace('.', '_').replace('-', '_') if intern.email else 'intern'
                    username = base_username
                    c = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{c}"
                        c += 1
                    cleaned_data['username'] = username

        elif volunteer:
            if volunteer.email and not cleaned_data.get('email'):
                cleaned_data['email'] = volunteer.email
            if volunteer.name:
                parts = volunteer.name.split()
                if not cleaned_data.get('first_name'):
                    cleaned_data['first_name'] = parts[0]
                if not cleaned_data.get('last_name') and len(parts) > 1:
                    cleaned_data['last_name'] = ' '.join(parts[1:])
                if not cleaned_data.get('username'):
                    base_username = volunteer.email.split('@')[0].replace('.', '_').replace('-', '_') if volunteer.email else 'volunteer'
                    username = base_username
                    c = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{c}"
                        c += 1
                    cleaned_data['username'] = username

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        intern = self.cleaned_data.get('intern_source')
        volunteer = self.cleaned_data.get('volunteer_source')

        if intern:
            if intern.email and not user.email:
                user.email = intern.email
            if intern.name:
                parts = intern.name.split()
                if not user.first_name:
                    user.first_name = parts[0]
                if not user.last_name and len(parts) > 1:
                    user.last_name = ' '.join(parts[1:])
            user.is_staff = True
        elif volunteer:
            if volunteer.email and not user.email:
                user.email = volunteer.email
            if volunteer.name:
                parts = volunteer.name.split()
                if not user.first_name:
                    user.first_name = parts[0]
                if not user.last_name and len(parts) > 1:
                    user.last_name = ' '.join(parts[1:])
            user.is_staff = True

        if commit:
            user.save()
            self.save_m2m()

            phone = None
            if intern and getattr(intern, 'contact_number', None):
                phone = intern.contact_number
            elif volunteer and getattr(volunteer, 'phone', None):
                phone = volunteer.phone

            if phone:
                profile, _ = StaffProfile.objects.get_or_create(user=user)
                profile.phone_number = phone
                profile.save()

            if intern:
                g, _ = Group.objects.get_or_create(name='Interns')
                user.groups.add(g)
            elif volunteer:
                g, _ = Group.objects.get_or_create(name='Volunteers')
                user.groups.add(g)

        return user

# Inline admin descriptor for StaffProfile model
class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile (Phone)'

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        ('Import from Application (Optional)', {
            'classes': ('wide',),
            'fields': ('intern_source', 'volunteer_source'),
            'description': 'Select an Intern or Volunteer to auto-populate email, name, phone, and assign to Interns/Volunteers group.'
        }),
        ('Account Credentials', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    inlines = (StaffProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    filter_horizontal = ('groups', 'user_permissions',)
    
    def get_phone(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Phone Number'

# Custom Group Admin Form with Users selection widget
from django.contrib.admin.widgets import FilteredSelectMultiple

class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Users', is_stacked=False),
        label="Group Members (Users)",
        help_text="Select users to include in this group."
    )

    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        group = super().save(commit=commit)
        if commit:
            self.save_m2m()
        return group

    def save_m2m(self):
        super().save_m2m()
        if 'users' in self.cleaned_data:
            self.instance.user_set.set(self.cleaned_data['users'])

# Custom Group Admin
class GroupAdmin(BaseGroupAdmin):
    form = GroupAdminForm
    filter_horizontal = ('users', 'permissions')
    list_display = ('name', 'user_count')

    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Members'

# Re-register User and Group
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'expiry_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('title', 'content')

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('staff', 'interaction_type', 'outcome', 'next_followup_date', 'created_at')
    list_filter = ('interaction_type', 'outcome') # Removed 'staff' to avoid loading all users
    search_fields = ('notes', 'staff__username', 'staff__first_name', 'staff__last_name', 'interaction_type', 'outcome')

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'city', 'phone', 'score', 'donation_count')
    search_fields = ('name', 'city', 'phone')
    list_filter = ('blood_group', 'city', 'consent_given')
    readonly_fields = ('score', 'donation_count')
    actions = ['recalculate_donor_stats']

    def recalculate_donor_stats(self, request, queryset):
        for donor in queryset:
            donations = donor.donations.all()
            donor.donation_count = donations.count()
            donor.score = sum(d.units for d in donations) * 10
            donor.save()
        self.message_user(request, f"Re-calculated donor metrics for {queryset.count()} records.")
    recalculate_donor_stats.short_description = "Recalculate selected donor stats"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('date',)
    filter_horizontal = ('managers',)
    exclude = ('slug',)

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.title)
            # Ensure uniqueness
            orig_slug = obj.slug
            counter = 1
            while Project.objects.filter(slug=obj.slug).exclude(pk=obj.pk).exists():
                obj.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save_model(request, obj, form, change)

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('contact_person', 'blood_group', 'city', 'units', 'status', 'created_at')
    list_filter = ('blood_group', 'city', 'status')
    readonly_fields = ('status',)
    actions = ['verify_request', 'fulfill_request', 'close_request']

    def verify_request(self, request, queryset):
        for obj in queryset:
            try:
                obj.verify()
                obj.save()
            except Exception as e:
                self.message_user(request, f"Error verifying {obj}: {str(e)}", level='ERROR')
    verify_request.short_description = "Verify selected blood requests"

    def fulfill_request(self, request, queryset):
        for obj in queryset:
            try:
                obj.start_fulfilling()
                obj.save()
            except Exception as e:
                self.message_user(request, f"Error starting fulfillment for {obj}: {str(e)}", level='ERROR')
    fulfill_request.short_description = "Mark selected requests as fulfilling"

    def close_request(self, request, queryset):
        for obj in queryset:
            try:
                obj.close()
                obj.save()
            except Exception as e:
                self.message_user(request, f"Error closing {obj}: {str(e)}", level='ERROR')
    close_request.short_description = "Close selected blood requests"

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 80px; border-radius: 4px; object-fit: cover;" />')
        return "-"
    image_preview.short_description = "Preview"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'gallery_count', 'created_at')
    search_fields = ('title', 'description', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('image_preview',)
    inlines = [BlogImageInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')},
    }

    def image_preview(self, obj):
        img_url = obj.cover_image_url
        if img_url:
            return mark_safe(f'<img src="{img_url}" style="max-height: 50px; max-width: 80px; border-radius: 4px; object-fit: cover;" />')
        return "-"
    image_preview.short_description = "Cover Preview"

    def gallery_count(self, obj):
        count = obj.images.count()
        return f"{count} gallery image(s)"
    gallery_count.short_description = "Gallery"





@admin.register(CampusAmbassador)
class CampusAmbassadorAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'city', 'created_at')
    search_fields = ('name', 'college')

@admin.register(CampusAmbassadorApplication)
class CampusAmbassadorApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'institution', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('full_name', 'email', 'institution')
    list_editable = ('status',)

@admin.register(NewsClipping)
class NewsClippingAdmin(admin.ModelAdmin):
    list_display = ('title', 'newspaper', 'date_display', 'created_at')
    search_fields = ('title', 'newspaper')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'subject', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('first_name', 'email', 'subject', 'message')
    actions = ['mark_as_read', 'mark_as_unread']

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message Snippet"

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active', 'created_at')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'description')

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'is_active', 'application_deadline', 'created_at')
    list_filter = ('job_type', 'is_active')
    search_fields = ('title', 'location', 'description')
    actions = ['activate_jobs', 'deactivate_jobs']

    def activate_jobs(self, request, queryset):
        queryset.update(is_active=True)
    activate_jobs.short_description = "Activate selected job postings"

    def deactivate_jobs(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_jobs.short_description = "Deactivate selected job postings"

# Registered missing internal portal and blog/newsletter models for admin visibility
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'date', 'units', 'created_at')
    search_fields = ('donor__name', 'notes')
    list_filter = ('date',)

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_task', 'assigned_to', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'parent_task__title')

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'task', 'created_at')
    search_fields = ('content', 'task__title', 'author__username')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)

@admin.register(SharedNote)
class SharedNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'parent_note', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('shared_with_teams', 'shared_with_users')

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name',)
    exclude = ('slug',)

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name)
            # Ensure uniqueness
            orig_slug = obj.slug
            counter = 1
            while Workspace.objects.filter(slug=obj.slug).exclude(pk=obj.pk).exists():
                obj.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save_model(request, obj, form, change)

@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'user', 'role', 'joined_at')
    list_filter = ('role',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'category', 'campaign', 'project', 'logged_by')
    list_filter = ('category', 'date')
    search_fields = ('title', 'notes', 'logged_by__username')

@admin.register(TaskAutomationRule)
class TaskAutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_type', 'action_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'trigger_type', 'action_type')
    search_fields = ('name',)

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('email',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('dependencies',)

# Custom Admin Grouping Configuration
GROUP_ORDER = [
    'Authentication & Authorization',
    'Blood Management',
    'Content Management',
    'Campaign Management',
    'Campus Ambassador',
    'Applications',
    'Communications',
    'Finance',
    'Reports & Documents',
    'Jobs & Careers',
    'Workspace Management',
]

GROUP_MAPPING = {
    'auth.user': 'Authentication & Authorization',
    'auth.group': 'Authentication & Authorization',
    'blood_request.blooddonor': 'Blood Management',
    'blood_request.bloodrequest': 'Blood Management',
    'blood_request.activity': 'Content Management',
    'blood_request.announcement': 'Content Management',
    'blood_request.blog': 'Content Management',
    'blood_request.newsclipping': 'Content Management',
    'blood_request.testimonial': 'Content Management',
    'blood_request.campaign': 'Campaign Management',
    'blood_request.project': 'Campaign Management',
    'blood_request.campusambassador': 'Campus Ambassador',
    'blood_request.campusambassadorapplication': 'Applications',
    'blood_request.internshiprequest': 'Applications',
    'blood_request.volunteerrequest': 'Applications',
    'blood_request.contactmessage': 'Communications',
    'blood_request.interaction': 'Communications',
    'blood_request.newslettersubscription': 'Communications',
    'blood_request.donation': 'Finance',
    'blood_request.expense': 'Finance',
    'blood_request.report': 'Reports & Documents',
    'blood_request.policyreport': 'Reports & Documents',
    'blood_request.jobposting': 'Jobs & Careers',
    'blood_request.workspace': 'Workspace Management',
    'blood_request.workspacemember': 'Workspace Management',
    'blood_request.team': 'Workspace Management',
    'blood_request.task': 'Workspace Management',
    'blood_request.subtask': 'Workspace Management',
    'blood_request.taskcomment': 'Workspace Management',
    'blood_request.taskautomationrule': 'Workspace Management',
    'blood_request.sharednote': 'Workspace Management',
}

original_get_app_list = admin.AdminSite.get_app_list

def custom_get_app_list(self, request, app_label=None):
    app_list = original_get_app_list(self, request, app_label)
    if app_label is not None:
        return app_list

    groups = {}
    for app in app_list:
        for model in app['models']:
            model_key = f"{app['app_label']}.{model['object_name']}".lower()
            group_name = GROUP_MAPPING.get(model_key)
            if not group_name:
                group_name = app['name']  # Fallback to original app section name

            if group_name not in groups:
                group_label = group_name.lower().replace(' & ', '_').replace(' ', '_')
                groups[group_name] = {
                    'name': group_name,
                    'app_label': group_label,
                    'app_url': app['app_url'] if group_name == 'Authentication & Authorization' else None,
                    'has_module_perms': True,
                    'models': []
                }
            groups[group_name]['models'].append(model)

    # Sort models within each group alphabetically
    for group in groups.values():
        group['models'].sort(key=lambda x: x['name'])

    # Build ordered list of groups
    sorted_groups = []
    for name in GROUP_ORDER:
        if name in groups:
            sorted_groups.append(groups[name])
    for name, group in groups.items():
        if name not in GROUP_ORDER:
            sorted_groups.append(group)

    return sorted_groups

# Inject custom method into the Django Admin class
admin.AdminSite.get_app_list = custom_get_app_list

# Dynamic AppConfig Proxy for Breadcrumbs
from django.db.models.options import Options

original_app_config_fget = Options.app_config.fget

class AppConfigProxy:
    def __init__(self, app_config, model):
        self._app_config = app_config
        self._model = model

    def __getattr__(self, name):
        if name == 'verbose_name':
            from blood_request.admin import GROUP_MAPPING
            model_key = f"{self._model._meta.app_label}.{self._model._meta.object_name}".lower()
            return GROUP_MAPPING.get(model_key, self._app_config.verbose_name)
        return getattr(self._app_config, name)

    def __str__(self):
        return getattr(self, 'verbose_name', str(self._app_config))


# ======================================================
# CUSTOM ADMIN DASHBOARD INDEX WRAPPER
# ======================================================

from django.db.models import Sum
original_admin_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    
    try:
        from django.contrib.auth.models import User
        from .models import (
            Campaign, BloodRequest, BloodDonor, VolunteerRequest, InternshipRequest,
            CampusAmbassadorApplication, ContactMessage, NewsletterSubscription,
            Task, Team, Workspace, Blog, NewsClipping, Activity, Project, Testimonial,
            Report, PolicyReport, JobPosting, Expense
        )

        def get_count(model, **kwargs):
            try:
                return model.objects.filter(**kwargs).count() if kwargs else model.objects.count()
            except Exception:
                return 0

        extra_context['kpi_total_users'] = get_count(User)
        extra_context['kpi_total_campaigns'] = get_count(Campaign)

        # Safe Campaign Status filter
        campaign_fields = [f.name for f in Campaign._meta.fields]
        if 'status' in campaign_fields:
            extra_context['kpi_pending_campaigns'] = get_count(Campaign, status__in=['Pending Review', 'Under Verification', 'Draft', 'Need Documents', 'pending', 'submitted', 'under_review'])
            extra_context['kpi_approved_campaigns'] = get_count(Campaign, status__in=['Approved', 'approved', 'published'])
            extra_context['kpi_rejected_campaigns'] = get_count(Campaign, status__in=['Rejected', 'rejected'])
        else:
            extra_context['kpi_pending_campaigns'] = 0
            extra_context['kpi_approved_campaigns'] = get_count(Campaign)
            extra_context['kpi_rejected_campaigns'] = 0

        extra_context['kpi_blood_requests'] = get_count(BloodRequest)
        extra_context['kpi_pending_blood'] = get_count(BloodRequest, status__in=['Received', 'Verified', 'Pending', 'pending'])
        extra_context['kpi_blood_donors'] = get_count(BloodDonor)
        
        extra_context['kpi_volunteer_requests'] = get_count(VolunteerRequest, status__iexact='pending')
        extra_context['kpi_internships'] = get_count(InternshipRequest, status__in=['Pending', 'Under Review', 'pending'])
        extra_context['kpi_campus_applications'] = get_count(CampusAmbassadorApplication, status__iexact='pending')

        try:
            raised_sum = Campaign.objects.aggregate(total=Sum('raised_amount'))['total'] or 0
        except Exception:
            raised_sum = 0
        extra_context['kpi_total_donations'] = raised_sum
        extra_context['kpi_donations_this_month'] = raised_sum

        extra_context['kpi_contact_messages'] = get_count(ContactMessage, is_read=False)
        extra_context['kpi_newsletter_subscribers'] = get_count(NewsletterSubscription)
        extra_context['kpi_tasks'] = get_count(Task)
        extra_context['kpi_teams'] = get_count(Team)
        extra_context['kpi_workspaces'] = get_count(Workspace)

        # Pending Approvals List
        try:
            if 'status' in campaign_fields:
                extra_context['pending_campaigns_list'] = Campaign.objects.filter(status__in=['Pending Review', 'Under Verification', 'Need Documents', 'Draft', 'submitted', 'under_review'])[:5]
            else:
                extra_context['pending_campaigns_list'] = Campaign.objects.all()[:5]
        except Exception:
            extra_context['pending_campaigns_list'] = []

        try:
            extra_context['pending_volunteers_list'] = VolunteerRequest.objects.filter(status__iexact='pending')[:5]
        except Exception:
            extra_context['pending_volunteers_list'] = []

        try:
            extra_context['pending_internships_list'] = InternshipRequest.objects.filter(status__in=['Pending', 'Under Review', 'pending'])[:5]
        except Exception:
            extra_context['pending_internships_list'] = []

        try:
            extra_context['pending_blood_list'] = BloodRequest.objects.filter(status__in=['Received', 'Verified', 'Pending', 'pending'])[:5]
        except Exception:
            extra_context['pending_blood_list'] = []

        # Recent Activities
        try: extra_context['recent_blogs_list'] = Blog.objects.order_by('-created_at')[:4]
        except Exception: pass
        try: extra_context['recent_news_list'] = NewsClipping.objects.order_by('-id')[:4]
        except Exception: pass
        try: extra_context['recent_messages_list'] = ContactMessage.objects.order_by('-created_at')[:4]
        except Exception: pass
        try: extra_context['recent_tasks_list'] = Task.objects.order_by('-id')[:4]
        except Exception: pass
    except Exception as e:
        pass

    return original_admin_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index


@admin.register(InternshipRequest)
class InternshipRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'internship_area', 'start_date', 'duration_months', 'status', 'created_at')
    list_filter = ('status', 'internship_area')
    search_fields = ('name', 'email', 'contact_number')
    readonly_fields = ('offer_letter', 'created_at')

    actions = ['approve_requests', 'create_user_accounts']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == 'Approved' and not obj.offer_letter:
            generate_internship_offer_letter(obj)

    @admin.action(description='Approve selected requests and generate offer letters')
    def approve_requests(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.status != 'Approved':
                obj.status = 'Approved'
                if not obj.offer_letter:
                    generate_internship_offer_letter(obj)
                obj.save()
                count += 1
        self.message_user(request, f"{count} internship request(s) were successfully approved and emails were sent.")

    @admin.action(description='Create User Account & assign to Interns group')
    def create_user_accounts(self, request, queryset):
        from django.contrib.auth.models import User, Group
        from .models import StaffProfile
        count = 0
        for intern in queryset:
            if not intern.email:
                continue
            email = intern.email.strip().lower()
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                base_username = email.split('@')[0].replace('.', '_').replace('-', '_')
                username = base_username
                c = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{c}"
                    c += 1

                parts = intern.name.split() if intern.name else ['Intern']
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Udaan@123',
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_active=True
                )
            profile, _ = StaffProfile.objects.get_or_create(user=user)
            if getattr(intern, 'contact_number', None) and not profile.phone_number:
                profile.phone_number = intern.contact_number
                profile.save()

            g, _ = Group.objects.get_or_create(name='Interns')
            user.groups.add(g)
            count += 1
        self.message_user(request, f"{count} User account(s) created/synced into 'Interns' group.")

@admin.register(VolunteerRequest)
class VolunteerRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'residence', 'education', 'employment', 'status', 'created_at')
    list_filter = ('status', 'education', 'employment')
    search_fields = ('name', 'email', 'phone', 'residence')
    readonly_fields = ('created_at',)
    actions = ['create_user_accounts']

    @admin.action(description='Create User Account & assign to Volunteers group')
    def create_user_accounts(self, request, queryset):
        from django.contrib.auth.models import User, Group
        from .models import StaffProfile
        count = 0
        for vol in queryset:
            if not vol.email:
                continue
            email = vol.email.strip().lower()
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                base_username = email.split('@')[0].replace('.', '_').replace('-', '_')
                username = base_username
                c = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{c}"
                    c += 1

                parts = vol.name.split() if vol.name else ['Volunteer']
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Udaan@123',
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_active=True
                )
            profile, _ = StaffProfile.objects.get_or_create(user=user)
            if getattr(vol, 'phone', None) and not profile.phone_number:
                profile.phone_number = vol.phone
                profile.save()

            g, _ = Group.objects.get_or_create(name='Volunteers')
            user.groups.add(g)
            count += 1
        self.message_user(request, f"{count} User account(s) created/synced into 'Volunteers' group.")

@property
def custom_app_config(self):
    app_config = original_app_config_fget(self)
    if app_config and hasattr(self, 'model'):
        return AppConfigProxy(app_config, self.model)
    return app_config

Options.app_config = custom_app_config


