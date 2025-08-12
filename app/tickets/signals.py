from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from .models import Role, UserMeta, Ticket, TicketResponse, TicketAction

# Map our custom permissions to Django's permission system
ROLE_PERMISSION_MAPPING = {
    'view_all_tickets': ['view_ticket'],
    'edit_all_tickets': ['change_ticket'],
    'assign_tickets': ['change_ticket'],
    'view_assigned_tickets': ['view_ticket'],
    'respond_to_tickets': ['add_ticketresponse', 'view_ticketresponse', 'change_ticketresponse'],
    'close_tickets': ['change_ticket'],
    'manage_users': ['view_user', 'change_user'],
    'manage_categories': ['add_ticketcategory', 'change_ticketcategory', 'view_ticketcategory'],
    'manage_faq': ['add_faqknowledgebase', 'change_faqknowledgebase', 'view_faqknowledgebase'],
}

@receiver(post_save, sender=UserMeta)
def update_user_permissions(sender, instance, created, **kwargs):
    """
    Updates a user's permissions based on their role and ensures staff status for support agents
    """
    if not instance.role:
        return
        
    user = instance.user
    
    # Set staff status for support agents
    if instance.role.name.lower() == 'support_agent' and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])
    
    # Clear existing permissions to prevent duplication
    user.user_permissions.clear()
    
    # Get all available django permissions
    all_perms = Permission.objects.all()
    
    # Get permissions from role
    role_perms = instance.role.get_permissions()
    permissions_to_add = set()
    
    # Map our custom permissions to Django permissions
    for role_perm in role_perms:
        if role_perm in ROLE_PERMISSION_MAPPING:
            for django_perm in ROLE_PERMISSION_MAPPING[role_perm]:
                # Get the app_label and permission codename
                parts = django_perm.split('_', 1)
                if len(parts) > 1:
                    action, model = parts[0], parts[1]
                    
                    matching_perms = Permission.objects.filter(
                        codename__startswith=action,
                        codename__endswith=model
                    )
                    
                    for perm in matching_perms:
                        permissions_to_add.add(perm)
    
    # Add ticket-specific permissions for support agents
    if instance.role.name.lower() == 'support_agent':
        # Get all the ticket-related models content types
        ticket_ct = ContentType.objects.get_for_model(Ticket)
        response_ct = ContentType.objects.get_for_model(TicketResponse)
        action_ct = ContentType.objects.get_for_model(TicketAction)
        
        # View permissions only for ticket and related models (NO CHANGE PERMISSIONS)
        view_perms = Permission.objects.filter(
            codename__startswith='view_',
            content_type__in=[ticket_ct, response_ct, action_ct]
        )
        permissions_to_add.update(view_perms)
        
        # Allow adding responses (but not changing tickets)
        add_response_perm = Permission.objects.filter(
            codename='add_ticketresponse',
            content_type=response_ct
        )
        permissions_to_add.update(add_response_perm)
        
        # Add ticket action permission (for internal notes only)
        add_action_perm = Permission.objects.filter(
            codename='add_ticketaction',
            content_type=action_ct
        )
        permissions_to_add.update(add_action_perm)
    
    # Apply the permissions
    for perm in permissions_to_add:
        user.user_permissions.add(perm)
