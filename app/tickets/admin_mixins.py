from django.contrib import admin
from django.db.models import Q

class SupportAgentAdminMixin:
    """
    Admin mixin to restrict what support agents can see in the admin panel
    """
    
    def get_queryset(self, request):
        """
        Override default queryset to restrict support agents to items they have permission to see
        """
        qs = super().get_queryset(request)
        
        # Superusers see everything
        if request.user.is_superuser:
            return qs
            
        # Check if this is a support agent
        try:
            role = request.user.user_meta.role
            if role and role.name.lower() == 'support_agent':
                # For tickets, show only tickets assigned to this agent
                if hasattr(self, 'model') and hasattr(self.model, 'assigned_to'):
                    return qs.filter(assigned_to=request.user)
                    
                # For ticket responses, show only responses related to tickets they are assigned to
                if hasattr(self, 'model') and hasattr(self.model, 'ticket'):
                    from .models import Ticket
                    viewable_tickets = Ticket.objects.filter(
                        assigned_to=request.user
                    ).values_list('id', flat=True)
                    return qs.filter(ticket__id__in=viewable_tickets)
                    
                # For ticket actions, show only actions related to tickets they are assigned to
                if hasattr(self, 'model') and hasattr(self.model, 'ticket'):
                    from .models import Ticket
                    viewable_tickets = Ticket.objects.filter(
                        assigned_to=request.user
                    ).values_list('id', flat=True)
                    return qs.filter(ticket__id__in=viewable_tickets)
        except Exception as e:
            # If there's an error, default to showing nothing for safety
            print(f"Error restricting admin view: {e}")
            if not request.user.is_superuser:
                return qs.none()
                
        return qs
        
    def has_change_permission(self, request, obj=None):
        """
        Determine whether a user has permission to change an object
        Support agents can't change any tickets - view only
        """
        # Superusers can change anything
        if request.user.is_superuser:
            return True
            
        # If we're not looking at a specific object, use the default permission
        if obj is None:
            return super().has_change_permission(request, obj)
            
        # Check if this is a support agent
        try:
            role = request.user.user_meta.role
            if role and role.name.lower() == 'support_agent':
                # Support agents cannot edit tickets
                if hasattr(obj, 'assigned_to'):
                    return False
                    
                # For ticket responses, they can only add new ones but not edit
                if hasattr(obj, 'user'):
                    return False
        except Exception:
            pass
            
        return super().has_change_permission(request, obj)
        
    def has_add_permission(self, request):
        """
        Support agents can only add responses, not tickets or other objects
        """
        # Superusers can add anything
        if request.user.is_superuser:
            return True
            
        # Check if this is a support agent
        try:
            role = request.user.user_meta.role
            if role and role.name.lower() == 'support_agent':
                # Allow adding responses only
                if hasattr(self, 'model') and self.model.__name__ == 'TicketResponse':
                    return True
                return False
        except Exception:
            pass
            
        return super().has_add_permission(request)
        
    def has_delete_permission(self, request, obj=None):
        """
        Support agents cannot delete any data
        """
        # By default, support agents cannot delete anything
        try:
            role = request.user.user_meta.role
            if role and role.name.lower() == 'support_agent':
                return False
        except Exception:
            pass
            
        return super().has_delete_permission(request, obj)
