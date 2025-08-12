import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Role, UserMeta

# Create admin role if it doesn't exist
admin_role, created = Role.objects.get_or_create(name='admin')
if created:
    print(f"Created admin role")
else:
    print(f"Admin role already exists")

# Create support_agent role if it doesn't exist
support_role, created = Role.objects.get_or_create(name='support_agent')
if created:
    print(f"Created support_agent role")
else:
    print(f"Support_agent role already exists")

# Create user role if it doesn't exist
user_role, created = Role.objects.get_or_create(name='user')
if created:
    print(f"Created user role")
else:
    print(f"User role already exists")

# Check if superuser exists
superuser_exists = User.objects.filter(is_superuser=True).exists()
if not superuser_exists:
    # Create superuser
    superuser = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    # Update user_meta to mark this user as an admin
    try:
        user_meta = UserMeta.objects.get(user=superuser)
        user_meta.role = admin_role
        user_meta.is_profile_completed = True
        user_meta.save()
    except UserMeta.DoesNotExist:
        UserMeta.objects.create(
            user=superuser,
            role=admin_role,
            is_profile_completed=True
        )
    print(f"Superuser 'admin' created with password 'admin123'")
else:
    print("Superuser already exists")

# Create a test support agent user
support_user_exists = User.objects.filter(username='support').exists()
if not support_user_exists:
    support_user = User.objects.create_user(
        username='support',
        email='support@example.com',
        password='support123'
    )
    # Mark this user as a support agent
    try:
        user_meta = UserMeta.objects.get(user=support_user)
        user_meta.role = support_role
        user_meta.is_profile_completed = True
        user_meta.save()
    except UserMeta.DoesNotExist:
        UserMeta.objects.create(
            user=support_user,
            role=support_role,
            is_profile_completed=True
        )
    print(f"Support agent 'support' created with password 'support123'")
else:
    print("Support user already exists")

# Create a test regular user
regular_user_exists = User.objects.filter(username='user').exists()
if not regular_user_exists:
    regular_user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='user123'
    )
    # Mark this user as a regular user
    try:
        user_meta = UserMeta.objects.get(user=regular_user)
        user_meta.role = user_role
        user_meta.is_profile_completed = True
        user_meta.save()
    except UserMeta.DoesNotExist:
        UserMeta.objects.create(
            user=regular_user,
            role=user_role,
            is_profile_completed=True
        )
    print(f"Regular user 'user' created with password 'user123'")
else:
    print("Regular user already exists")
