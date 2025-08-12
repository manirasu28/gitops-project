from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django import forms

from .models import (
    Role, UserMeta, Ticket, TicketCategory, 
    TicketResponse, TicketAction, Media, FAQKnowledgeBase
)
from .admin_mixins import SupportAgentAdminMixin

# Define inline admin for UserMeta
class UserMetaInline(admin.StackedInline):
    model = UserMeta
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['first_name', 'last_name', 'gender', 'contact_number', 'location', 'role', 'is_profile_completed']

# Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserMetaInline]
    list_display = ['username', 'email', 'get_role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'user_meta__role']
    
    def get_role(self, obj):
        try:
            return obj.user_meta.role.name if obj.user_meta.role else 'No role'
        except UserMeta.DoesNotExist:
            return 'No profile'
    get_role.short_description = 'Role'

    def has_view_permission(self, request, obj=None):
        # Everyone can view user list
        return True
        
    def has_change_permission(self, request, obj=None):
        # Can edit if: it's your own profile, you're a superuser, or you're an admin
        if obj is None:  # List view
            return True
            
        # Allow editing your own profile
        if obj == request.user:
            return True
            
        # Superusers can edit anyone
        if request.user.is_superuser:
            return True
            
        # Check for admin role
        try:
            role = request.user.user_meta.role.name.lower()
            if role == 'admin':
                return True
        except:
            pass
            
        return False

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Ticket Response Inline
class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    fields = ['user', 'message', 'created_at']
    readonly_fields = ['created_at']

# Ticket Action Inline
class TicketActionInline(admin.TabularInline):
    model = TicketAction
    extra = 0
    fields = ['action_type', 'performed_by', 'action_taken', 'resolution_summary', 'notes', 'created_at']
    readonly_fields = ['action_type', 'performed_by', 'action_taken', 'resolution_summary', 'notes', 'created_at']
    can_delete = False
    max_num = 0  # Prevents adding new actions through the admin
    template = 'admin/tickets/ticket/ticket_action_inline.html'
    verbose_name = "Ticket Action"
    verbose_name_plural = "Ticket Actions"
    
    def get_queryset(self, request):
        # Override queryset to ensure all actions are shown
        qs = super().get_queryset(request)
        return qs.select_related('performed_by').order_by('-created_at')
    
    def has_add_permission(self, request, obj=None):
        # Prevent adding actions directly from the ticket admin
        return False
        
    def has_change_permission(self, request, obj=None):
        # Make actions read-only to prevent modification
        return False

# Media Inline
class MediaInline(admin.TabularInline):
    model = Media
    extra = 0

# Role Admin
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_permissions_display']
    search_fields = ['name']
    
    def get_permissions_display(self, obj):
        if not obj.permissions:
            return "No permissions assigned"
        permissions = obj.get_permissions()
        if not permissions:
            return "No permissions assigned"
        return ", ".join(permissions)
    
    def get_form(self, request, obj=None, **kwargs):
        class RoleAdminForm(forms.ModelForm):
            # Create a multiple choice field for permissions
            AVAILABLE_PERMISSIONS = [
                ('view_all_tickets', 'View all tickets'),
                ('edit_all_tickets', 'Edit all tickets'),
                ('assign_tickets', 'Assign tickets to support agents'),
                ('respond_to_tickets', 'Respond to tickets'),
                ('close_tickets', 'Close tickets'),
                ('view_assigned_tickets', 'View assigned tickets'),
                ('manage_users', 'Manage users'),
                ('manage_categories', 'Manage ticket categories'),
                ('manage_faq', 'Manage FAQ/Knowledge Base'),
            ]
            
            permissions_list = forms.MultipleChoiceField(
                choices=AVAILABLE_PERMISSIONS,
                widget=forms.CheckboxSelectMultiple,
                required=False,
                help_text="Select permissions for this role"
            )
            
            class Meta:
                model = Role
                fields = ['name']
                
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.instance and self.instance.pk:
                    self.fields['permissions_list'].initial = self.instance.get_permissions()
                    
            def save(self, commit=True):
                instance = super().save(commit=False)
                if commit:
                    instance.save()
                    # Save permissions
                    if 'permissions_list' in self.cleaned_data:
                        if self.cleaned_data['permissions_list']:
                            instance.permissions = ','.join(self.cleaned_data['permissions_list'])
                        else:
                            instance.permissions = ''
                        instance.save()
                return instance
                
        return RoleAdminForm

# Ticket Category Admin
@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

# Ticket Admin
@admin.register(Ticket)
class TicketAdmin(SupportAgentAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['id', 'title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'assigned_to']
    inlines = [TicketResponseInline, TicketActionInline, MediaInline]
    actions = ['mark_as_resolved', 'assign_to_support']
    fieldsets = [
        ('Basic Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Status and Assignment', {
            'fields': ('status', 'priority', 'category', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            # Only show support agents in the assigned_to dropdown
            support_role = Role.objects.filter(name__icontains="support").first()
            if support_role:
                kwargs["queryset"] = User.objects.filter(user_meta__role=support_role)
            else:
                kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Check if this is a TicketAction instance and set performed_by
            if isinstance(instance, TicketAction) and not instance.performed_by_id:
                instance.performed_by = request.user
            instance.save()
        formset.save_m2m()
        
    def save_model(self, request, obj, form, change):
        # Track status changes with ticket actions
        if change and form.has_changed() and 'status' in form.changed_data:
            try:
                TicketAction.objects.create(
                    ticket=obj,
                    performed_by=request.user,
                    action_type='status_change',
                    notes=f"Status changed to {obj.get_status_display()}"
                )
            except Exception as e:
                # Log the error but continue saving
                print(f"Error creating status change action: {e}")
                
        # Track assignment changes
        if change and form.has_changed() and 'assigned_to' in form.changed_data:
            try:
                TicketAction.objects.create(
                    ticket=obj,
                    performed_by=request.user,
                    action_type='assign',
                    notes=f"Ticket assigned to {obj.assigned_to.username if obj.assigned_to else 'nobody'}"
                )
            except Exception as e:
                # Log the error but continue saving
                print(f"Error creating assignment action: {e}")
        
        super().save_model(request, obj, form, change)
        
    def assign_to_support(self, request, queryset):
        # Implementation for bulk assignment
        for ticket in queryset:
            # Logic to assign to a support agent
            pass
            
    assign_to_support.short_description = "Assign selected tickets to support agent"
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        # Create ticket actions for bulk resolution
        for ticket in queryset:
            try:
                TicketAction.objects.create(
                    ticket=ticket,
                    performed_by=request.user,
                    action_type='status_change',
                    notes="Ticket marked as resolved (bulk action)"
                )
            except Exception as e:
                # Log error but continue
                print(f"Error creating bulk resolve action: {e}")
                
        self.message_user(request, f"{updated} tickets have been marked as resolved.")

# TicketResponse Admin
@admin.register(TicketResponse)
class TicketResponseAdmin(SupportAgentAdminMixin, admin.ModelAdmin):
    list_display = ['ticket', 'user', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['message', 'ticket__title']
    readonly_fields = ['created_at', 'updated_at']

# TicketAction Admin
@admin.register(TicketAction)
class TicketActionAdmin(SupportAgentAdminMixin, admin.ModelAdmin):
    list_display = ['ticket', 'performed_by', 'action_type', 'action_taken', 'created_at']
    list_filter = ['action_type', 'created_at', 'performed_by']
    search_fields = ['notes', 'action_taken', 'resolution_summary', 'ticket__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ('ticket', 'performed_by', 'action_type')
        }),
        ('Action Details', {
            'fields': ('action_taken', 'resolution_summary', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        # Set performed_by to the current user
        if not change:  # Only for new records
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)

# Media Admin
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['file', 'ticket', 'user', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['file', 'ticket__title', 'user__username']
    readonly_fields = ['uploaded_at']

# FAQ/KnowledgeBase Admin
@admin.register(FAQKnowledgeBase)
class FAQKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_published', 'order']
    list_filter = ['category', 'is_published']
    search_fields = ['question', 'answer']
    list_editable = ['is_published', 'order', 'category']
