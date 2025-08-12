import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Import models
from django.db import connection
from django.contrib.auth.models import User

def fix_ticket_actions_table():
    print("Checking and fixing TicketAction table structure...")
    with connection.cursor() as cursor:
        # Get the admin user to use as default performer
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
            
        if not admin_user:
            print("Error: No users found in database!")
            return
            
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets_ticketaction'")
        if not cursor.fetchone():
            print("TicketAction table doesn't exist! Creating it...")
            cursor.execute("""
                CREATE TABLE tickets_ticketaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL REFERENCES tickets_ticket(id),
                    performed_by_id INTEGER NOT NULL REFERENCES auth_user(id),
                    action_type VARCHAR(20) NOT NULL,
                    notes TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created new tickets_ticketaction table")
            return
            
        # Check columns
        cursor.execute("PRAGMA table_info(tickets_ticketaction)")
        columns = {column[1]: column for column in cursor.fetchall()}
        
        if 'performed_by_id' not in columns:
            print("Missing performed_by_id column, recreating table...")
            
            # Backup existing data
            cursor.execute("CREATE TABLE tickets_ticketaction_backup AS SELECT * FROM tickets_ticketaction")
            print("Created backup of existing data")
            
            # Drop and recreate table with correct structure
            cursor.execute("DROP TABLE tickets_ticketaction")
            cursor.execute("""
                CREATE TABLE tickets_ticketaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL REFERENCES tickets_ticket(id),
                    performed_by_id INTEGER NOT NULL REFERENCES auth_user(id),
                    action_type VARCHAR(20) NOT NULL,
                    notes TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Try to restore data if user_id column existed
            if 'user_id' in columns:
                print("Attempting to migrate data from user_id to performed_by_id...")
                try:
                    cursor.execute("""
                        INSERT INTO tickets_ticketaction (id, ticket_id, performed_by_id, action_type, notes, created_at)
                        SELECT id, ticket_id, user_id, action_type, notes, created_at FROM tickets_ticketaction_backup
                    """)
                    print("Data migration successful")
                except Exception as e:
                    print(f"Data migration failed: {e}")
                    print(f"Setting default admin user (id: {admin_user.id}) for all actions")
                    cursor.execute("""
                        INSERT INTO tickets_ticketaction (ticket_id, performed_by_id, action_type, notes, created_at)
                        SELECT ticket_id, ?, action_type, notes, created_at FROM tickets_ticketaction_backup
                    """, [admin_user.id])
            else:
                print("No user_id column found, setting default admin user for all actions")
                try:
                    cursor.execute("""
                        INSERT INTO tickets_ticketaction (ticket_id, performed_by_id, action_type, notes, created_at)
                        SELECT ticket_id, ?, action_type, notes, created_at FROM tickets_ticketaction_backup
                    """, [admin_user.id])
                except Exception as e:
                    print(f"Error restoring data: {e}")
                    
            print("Table recreation complete!")
        else:
            # Check for NULL values in performed_by_id
            cursor.execute("SELECT COUNT(*) FROM tickets_ticketaction WHERE performed_by_id IS NULL")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                print(f"Fixing {null_count} NULL values in performed_by_id...")
                cursor.execute("UPDATE tickets_ticketaction SET performed_by_id = ? WHERE performed_by_id IS NULL", [admin_user.id])
                print("Fixed NULL values")
            else:
                print("No NULL values found in performed_by_id")
                
        print("TicketAction table structure appears to be correct.")

if __name__ == "__main__":
    fix_ticket_actions_table()
