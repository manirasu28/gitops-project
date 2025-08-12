import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Timeout in seconds to wait for database'
        )

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        timeout = options['timeout']
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        
        self.stdout.write(
            self.style.ERROR(f'Database not available after {timeout} seconds')
        )
        raise Exception('Database connection timeout') 