import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Now import Django models
from tickets.models import Role

# Create roles if they don't exist
def create_roles():
    # Define all roles needed in the system
    roles = [
        {
            'name': 'user',
            'permissions': 'Can create and view own tickets, update profile, view FAQ'
        },
        {
            'name': 'support_agent',
            'permissions': 'Can respond to assigned tickets, update assigned ticket status'
        },
        {
            'name': 'admin',
            'permissions': 'Full access to all system features and user management'
        }
    ]
    
    # Create roles if they don't exist
    for role_data in roles:
        role, created = Role.objects.get_or_create(name=role_data['name'])
        if created:
            role.permissions = role_data['permissions']
            role.save()
            print(f"Created role: {role.name}")
        else:
            print(f"Role already exists: {role.name}")

if __name__ == '__main__':
    print("Creating roles...")
    create_roles()
    print("Done!")
