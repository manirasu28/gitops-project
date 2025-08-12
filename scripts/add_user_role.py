import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Now import Django models
from tickets.models import Role

def add_user_role():
    # Define the user role
    user_role_data = {
        'name': 'user',
        'permissions': 'view_assigned_tickets,respond_to_tickets'
    }
    
    # Create the user role if it doesn't exist
    role, created = Role.objects.get_or_create(name=user_role_data['name'])
    if created:
        role.permissions = user_role_data['permissions']
        role.save()
        print(f"Created new role: {role.name}")
    else:
        print(f"Role already exists: {role.name}")
        
    # Check if there are any existing users with customer role that need to be updated
    customer_role = Role.objects.filter(name='customer').first()
    if customer_role:
        from django.contrib.auth.models import User
        from tickets.models import UserMeta
        
        # Get count of users with customer role
        customer_users_count = UserMeta.objects.filter(role=customer_role).count()
        print(f"Found {customer_users_count} users with 'customer' role")
        
        # Ask if we should update existing users
        print("\nNOTE: New users will now be assigned the 'user' role by default.")
        print("The 'customer' role still exists in the system for backward compatibility.")

if __name__ == '__main__':
    print("Adding 'user' role to the system...")
    add_user_role()
    print("\nDone! New users will now be assigned the 'user' role by default.")
