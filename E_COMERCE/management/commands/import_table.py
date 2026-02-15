import csv
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Import CSV file into specific table'

    def add_arguments(self, parser):
        parser.add_argument('table_name', type=str, help='Table name to import into')
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--truncate', action='store_true', help='Clear table before import')

    def handle(self, *args, **options):
        table_name = options['table_name']
        csv_file = options['csv_file']
        truncate = options['truncate']
        
        # Optional: Clear existing data
        if truncate:
            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            self.stdout.write(f'Cleared existing data from {table_name}')
        
        # Import CSV using PostgreSQL COPY (fastest method)
        with open(csv_file, 'r', encoding='utf-8') as f:
            with connection.cursor() as cursor:
                cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
        
        self.stdout.write(self.style.SUCCESS(f'Imported {csv_file} into {table_name}'))
