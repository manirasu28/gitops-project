from django import template
from django.contrib.auth.models import User
from ..models import Role

register = template.Library()

@register.simple_tag
def get_support_agents():
    """
    Returns a queryset of all support agents.
    For use in ticket assignment forms.
    """
    support_role = Role.objects.filter(name='support').first()
    if support_role:
        return User.objects.filter(user_meta__role=support_role)
    return User.objects.none()

@register.filter
def get_item(dictionary, key):
    """
    Returns the value for a key in a dictionary.
    Useful for accessing dictionary values in templates.
    """
    return dictionary.get(key)

@register.simple_tag
def get_ticket_status_class(status):
    """
    Returns the appropriate Bootstrap class for a ticket status.
    """
    status_classes = {
        'pending': 'bg-warning text-dark',
        'in_progress': 'bg-info text-dark',
        'resolved': 'bg-success',
        'closed': 'bg-secondary'
    }
    return status_classes.get(status, 'bg-secondary')

@register.simple_tag
def get_ticket_priority_class(priority):
    """
    Returns the appropriate Bootstrap class for a ticket priority.
    """
    priority_classes = {
        'low': 'bg-success',
        'medium': 'bg-info',
        'high': 'bg-warning text-dark',
        'urgent': 'bg-danger'
    }
    return priority_classes.get(priority, 'bg-secondary')
