from django.core.management.base import BaseCommand
from tickets.models import Role, UserMeta, Ticket, TicketResponse, TicketAction
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates or updates the support_agent role with necessary permissions and updates user staff status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--assign',
            action='store',
            dest='assign_username',
            help='Assign support_agent role to a specific user by username',
        )
        
        parser.add_argument(
            '--update-all',
            action='store_true',
            dest='update_all',
            help='Update all users with support_agent role to have staff status and correct permissions',
        )
    
    def handle(self, *args, **options):
        with transaction.atomic():
            # Check if support_agent role exists
            support_role, created = Role.objects.get_or_create(
                name='support_agent',
                defaults={
                    'permissions': 'view_assigned_tickets,respond_to_tickets,view_all_tickets,close_tickets'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Support Agent role created successfully!'))
            else:
                # Update permissions if role already exists (using direct SQL to avoid signal recursion)
                from django.db import connection
                current_permissions = set(support_role.get_permissions())
                
                # Define the permissions support agents should have
                required_permissions = {
                    'view_assigned_tickets',  # Can view tickets assigned to them
                    'respond_to_tickets',     # Can respond to tickets
                    'view_all_tickets',       # Can view all tickets in the system
                    'close_tickets',          # Can close tickets
                }
                
                # Add any missing permissions
                missing_permissions = required_permissions - current_permissions
                if missing_permissions:
                    all_permissions = current_permissions.union(required_permissions)
                    perms_str = ','.join(all_permissions)
                    
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE tickets_role SET permissions = %s WHERE id = %s",
                            [perms_str, support_role.id]
                        )
                    
                    support_role.refresh_from_db()
                    self.stdout.write(self.style.SUCCESS('Support Agent role updated with required permissions!'))
                else:
                    self.stdout.write(self.style.SUCCESS('Support Agent role already has all required permissions'))
            
            # Get Django model permissions that support agents need
            self.stdout.write("Setting up Django model permissions for support agents...")
            django_permissions = self.get_support_agent_permissions()
            
            # Assign role to a specific user if requested
            if options['assign_username']:
                try:
                    user = User.objects.get(username=options['assign_username'])
                    
                    # Ensure user has UserMeta
                    user_meta, created = UserMeta.objects.get_or_create(user=user)
                    
                    # Assign the role
                    user_meta.role = support_role
                    user_meta.save()
                    
                    # Make sure user is staff
                    if not user.is_staff:
                        user.is_staff = True
                        user.save(update_fields=['is_staff'])
                    
                    # Add Django permissions
                    self.apply_django_permissions(user, django_permissions)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"User '{user.username}' has been assigned the support_agent role with {len(django_permissions)} Django permissions"
                    ))
                    
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User '{options['assign_username']}' not found"))
            
            # Update all users with support_agent role
            if options['update_all']:
                support_users = UserMeta.objects.filter(role=support_role)
                count = 0
                perm_count = 0
                
                for user_meta in support_users:
                    user = user_meta.user
                    
                    # Set staff status
                    if not user.is_staff:
                        user.is_staff = True
                        user.save(update_fields=['is_staff'])
                        count += 1
                    
                    # Add Django permissions
                    perm_added = self.apply_django_permissions(user, django_permissions)
                    perm_count += perm_added
                
                if count > 0:
                    self.stdout.write(self.style.SUCCESS(f"Updated {count} support agents to have admin access"))
                
                if perm_count > 0:
                    self.stdout.write(self.style.SUCCESS(f"Added {perm_count} Django permissions to support agents"))
                
                if count == 0 and perm_count == 0:
                    self.stdout.write(self.style.SUCCESS("All support agents already have correct access and permissions"))
            
            # Output the final permissions for verification
            self.stdout.write(f"Support Agent role permissions: {support_role.permissions}")
    
    def get_support_agent_permissions(self):
        """Get the Django model permissions that support agents need"""
        permissions = []
        
        # Get content types for models support agents need access to
        content_types = [
            ContentType.objects.get_for_model(Ticket),
            ContentType.objects.get_for_model(TicketResponse),
            ContentType.objects.get_for_model(TicketAction)
        ]
        
        # Add view permissions for all models
        for ct in content_types:
            view_perm = Permission.objects.get(
                content_type=ct,
                codename=f'view_{ct.model}'
            )
            permissions.append(view_perm)
        
        # Support agents can only view tickets, but not change them
        # We've removed the change_ticket permission
        
        # Add add permission for responses (they can respond but not edit)
        response_ct = ContentType.objects.get_for_model(TicketResponse)
        add_response = Permission.objects.get(
            content_type=response_ct,
            codename='add_ticketresponse'
        )
        permissions.append(add_response)
        
        # Add add permission for ticket actions (for internal notes only)
        action_ct = ContentType.objects.get_for_model(TicketAction)
        add_action = Permission.objects.get(
            content_type=action_ct,
            codename='add_ticketaction'
        )
        permissions.append(add_action)
        
        return permissions
    
    def apply_django_permissions(self, user, permissions):
        """Apply Django permissions to the user"""
        added_count = 0
        
        # First clear existing permissions to avoid duplicates
        user.user_permissions.clear()
        
        # Then add the required permissions
        for perm in permissions:
            user.user_permissions.add(perm)
            added_count += 1
        
        return added_count
