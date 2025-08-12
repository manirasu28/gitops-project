from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.contrib.auth.models import User
from tickets.models import TicketAction

class Command(BaseCommand):
    help = 'Fix TicketAction table structure issues'

    def handle(self, *args, **options):
        self.stdout.write('Starting TicketAction table fixes...')
        
        with connection.cursor() as cursor:
            # Get current schema information
            cursor.execute("PRAGMA table_info(tickets_ticketaction)")
            columns = {column[1]: column for column in cursor.fetchall()}
            
            # Make a backup of the table first
            self.stdout.write('Creating backup of tickets_ticketaction table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets_ticketaction_backup AS 
                SELECT * FROM tickets_ticketaction
            """)
            
            # Check if we need to fix the performed_by_id column
            if 'performed_by_id' not in columns:
                self.stdout.write('The performed_by_id column is missing, creating a new table with proper structure...')
                
                # Get default user for migration
                default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                
                if not default_user:
                    self.stdout.write(self.style.ERROR('No user found to use as default for performed_by'))
                    return
                    
                # Drop and recreate the table with the correct structure
                with transaction.atomic():
                    # Create new table with correct structure
                    cursor.execute("""
                        CREATE TABLE tickets_ticketaction_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticket_id INTEGER NOT NULL REFERENCES tickets_ticket(id),
                            performed_by_id INTEGER REFERENCES auth_user(id),
                            action_type VARCHAR(20) NOT NULL,
                            notes TEXT,
                            created_at DATETIME NOT NULL
                        )
                    """)
                    
                    # Migrate data, using user_id as performed_by_id if it exists
                    if 'user_id' in columns:
                        cursor.execute(f"""
                            INSERT INTO tickets_ticketaction_new (id, ticket_id, performed_by_id, action_type, notes, created_at)
                            SELECT id, ticket_id, user_id, action_type, notes, created_at FROM tickets_ticketaction
                        """)
                    else:
                        cursor.execute(f"""
                            INSERT INTO tickets_ticketaction_new (id, ticket_id, performed_by_id, action_type, notes, created_at)
                            SELECT id, ticket_id, {default_user.id}, action_type, notes, created_at FROM tickets_ticketaction
                        """)
                    
                    # Replace the old table with the new one
                    cursor.execute("DROP TABLE tickets_ticketaction")
                    cursor.execute("ALTER TABLE tickets_ticketaction_new RENAME TO tickets_ticketaction")
                
                self.stdout.write(self.style.SUCCESS('Successfully recreated tickets_ticketaction table'))
            else:
                self.stdout.write('performed_by_id column exists, checking for NULL values...')
                
                # Get default user for NULL values
                default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                
                if default_user:
                    # Update any NULL performed_by_id values
                    cursor.execute(f"""
                        UPDATE tickets_ticketaction 
                        SET performed_by_id = {default_user.id} 
                        WHERE performed_by_id IS NULL
                    """)
                    self.stdout.write(f'Updated NULL performed_by_id values to user {default_user.username}')
                
            # Create any missing indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS tickets_ticketaction_performed_by_id_idx
                ON tickets_ticketaction(performed_by_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS tickets_ticketaction_ticket_id_idx
                ON tickets_ticketaction(ticket_id)
            """)
        
        self.stdout.write(self.style.SUCCESS('Database fixes completed! Try using the admin interface now.'))
