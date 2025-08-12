from django.db import migrations

def forward_func(apps, schema_editor):
    # Get the Role model from our migrations
    Role = apps.get_model('tickets', 'Role')
    UserMeta = apps.get_model('tickets', 'UserMeta')
    
    # Remove 'support' role and convert any users with that role to 'support_agent'
    try:
        support_role = Role.objects.filter(name='support').first()
        support_agent_role = Role.objects.filter(name='support_agent').first()
        
        if support_role and support_agent_role:
            # Update all users with support role to support_agent
            UserMeta.objects.filter(role=support_role).update(role=support_agent_role)
            # Delete the support role
            support_role.delete()
        elif support_role and not support_agent_role:
            # Just rename the role
            support_role.name = 'support_agent'
            # Set default permissions
            support_role.permissions = 'respond_to_tickets,view_assigned_tickets,close_tickets'
            support_role.save()
    except Exception as e:
        print(f"Error updating roles: {e}")
    
    # Update permission strings for existing roles
    admin_role = Role.objects.filter(name='admin').first()
    if admin_role:
        # Set full permissions for admin
        admin_role.permissions = 'view_all_tickets,edit_all_tickets,assign_tickets,respond_to_tickets,close_tickets,manage_users,manage_categories,manage_faq'
        admin_role.save()
    
    support_agent = Role.objects.filter(name='support_agent').first()
    if support_agent and not support_agent.permissions:
        # Set appropriate permissions for support_agent
        support_agent.permissions = 'respond_to_tickets,view_assigned_tickets,close_tickets'
        support_agent.save()
    
    customer_role = Role.objects.filter(name='customer').first()
    if customer_role:
        # Basic customer permissions
        customer_role.permissions = ''
        customer_role.save()

def reverse_func(apps, schema_editor):
    # We don't need to reverse this migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0004_alter_faqknowledgebase_options_websitecontent'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
