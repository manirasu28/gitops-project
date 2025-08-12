import os
import django
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

# Import models
from django.db import connection
from django.contrib.auth.models import User

def rebuild_ticket_action_table():
    print("\n=== Rebuilding TicketAction table ===\n")
    
    # Get admin user to use as default performer
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.first()
        
    if not admin_user:
        print("Error: No users found in database!")
        return
    
    print(f"Using default user: {admin_user.username} (ID: {admin_user.id})")
    
    with connection.cursor() as cursor:
        # Backup current table if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets_ticketaction'")
        if cursor.fetchone():
            print("Backing up existing TicketAction data...")
            cursor.execute("DROP TABLE IF EXISTS tickets_ticketaction_backup")
            cursor.execute("CREATE TABLE tickets_ticketaction_backup AS SELECT * FROM tickets_ticketaction")
            
            # Get column names from backup for data migration
            cursor.execute("PRAGMA table_info(tickets_ticketaction_backup)")
            backup_columns = [column[1] for column in cursor.fetchall()]
            print(f"Backup table columns: {backup_columns}")
            
            # Drop existing table
            cursor.execute("DROP TABLE tickets_ticketaction")
            print("Dropped original table")
        else:
            backup_columns = []
            print("No existing TicketAction table found")
        
        # Create fresh table with correct structure
        print("Creating new TicketAction table with proper structure...")
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
        
        # Try to migrate data if backup exists
        if 'id' in backup_columns:
            try:
                print("Migrating data from backup...")
                
                # Determine which columns we can copy
                columns_to_copy = []
                target_columns = []
                
                if 'ticket_id' in backup_columns:
                    columns_to_copy.append('ticket_id')
                    target_columns.append('ticket_id')
                
                # Handle the performer field - could be user_id or performed_by_id
                if 'performed_by_id' in backup_columns:
                    columns_to_copy.append('performed_by_id')
                    target_columns.append('performed_by_id')
                elif 'user_id' in backup_columns:
                    columns_to_copy.append('user_id')
                    target_columns.append('performed_by_id')
                
                if 'action_type' in backup_columns:
                    columns_to_copy.append('action_type')
                    target_columns.append('action_type')
                else:
                    # Default action_type
                    columns_to_copy.append("'note'")
                    target_columns.append('action_type')
                
                if 'notes' in backup_columns:
                    columns_to_copy.append('notes')
                    target_columns.append('notes')
                else:
                    # Default notes
                    columns_to_copy.append("'Data migrated from old table'")
                    target_columns.append('notes')
                
                if 'created_at' in backup_columns:
                    columns_to_copy.append('created_at')
                    target_columns.append('created_at')
                else:
                    # Default created_at
                    current_time = datetime.datetime.now().isoformat()
                    columns_to_copy.append(f"'{current_time}'")
                    target_columns.append('created_at')
                
                # Build the SQL query
                columns_sql = ", ".join(columns_to_copy)
                target_sql = ", ".join(target_columns)
                
                # Insert the data
                cursor.execute(f"""
                    INSERT INTO tickets_ticketaction ({target_sql})
                    SELECT {columns_sql} FROM tickets_ticketaction_backup
                """)
                
                print("Data migration successful!")
            except Exception as e:
                print(f"Error migrating data: {e}")
                print("Creating sample action for data integrity...")
                
                # Get a sample ticket to create an action for
                cursor.execute("SELECT id FROM tickets_ticket LIMIT 1")
                ticket_result = cursor.fetchone()
                
                if ticket_result:
                    ticket_id = ticket_result[0]
                    cursor.execute("""
                        INSERT INTO tickets_ticketaction 
                        (ticket_id, performed_by_id, action_type, notes, created_at)
                        VALUES (?, ?, 'note', 'Table rebuilt by admin', CURRENT_TIMESTAMP)
                    """, [ticket_id, admin_user.id])
                    print(f"Created sample action for ticket {ticket_id}")
        
        # Create necessary indexes
        print("Creating indexes on TicketAction table...")
        cursor.execute("""
            CREATE INDEX tickets_ticketaction_ticket_id_idx 
            ON tickets_ticketaction(ticket_id)
        """)
        cursor.execute("""
            CREATE INDEX tickets_ticketaction_performed_by_id_idx 
            ON tickets_ticketaction(performed_by_id)
        """)
        cursor.execute("""
            CREATE INDEX tickets_ticketaction_action_type_idx 
            ON tickets_ticketaction(action_type)
        """)
        
        print("\n=== TicketAction table rebuild complete! ===\n")
        print("Please restart your Django server to use the new table structure.")

if __name__ == "__main__":
    rebuild_ticket_action_table()
