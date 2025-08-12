import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Now we can import Django models
from django.db import connection
from tickets.models import TicketAction
from django.contrib.auth.models import User

def fix_database():
    # Get admin user to use as default performer
    default_user = User.objects.filter(is_superuser=True).first()
    if not default_user:
        default_user = User.objects.first()
    
    if not default_user:
        print("Error: No users found in database to use as default performer")
        return
    
    # Check if performed_by_id column exists
    with connection.cursor() as cursor:
        # Get table info
        cursor.execute("PRAGMA table_info(tickets_ticketaction)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'performed_by_id' not in columns:
            print("Adding performed_by_id column to tickets_ticketaction table...")
            # Add performed_by_id column
            cursor.execute(f"ALTER TABLE tickets_ticketaction ADD COLUMN performed_by_id integer REFERENCES auth_user(id)")
            # Set default value
            cursor.execute(f"UPDATE tickets_ticketaction SET performed_by_id = {default_user.id}")
            print(f"Set default performer to user: {default_user.username}")
        else:
            print("performed_by_id column already exists")
            
        # Check if user_id column exists and needs to be migrated
        if 'user_id' in columns:
            print("Migrating data from user_id to performed_by_id...")
            # Copy user_id values to performed_by_id where performed_by_id is NULL
            cursor.execute("UPDATE tickets_ticketaction SET performed_by_id = user_id WHERE performed_by_id IS NULL")
            print("Data migration complete")

    print("Database fix completed!")

if __name__ == "__main__":
    fix_database()
