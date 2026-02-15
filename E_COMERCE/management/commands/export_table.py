import csv
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Export specific table to CSV'

    def add_arguments(self, parser):
        parser.add_argument('table_name', type=str, help='Table name to export')
        parser.add_argument('--filename', type=str, default=None, help='Output filename')

    def handle(self, *args, **options):
        table_name = options['table_name']
        filename = options['filename'] or f"{table_name}.csv"
        
        with connection.cursor() as cursor:
            # Get column names
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position")
            columns = [row[0] for row in cursor.fetchall()]
            
            # Export data
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)  # Header
                
                cursor.copy_expert(f"COPY {table_name} TO STDOUT WITH CSV HEADER", f)
        
        self.stdout.write(self.style.SUCCESS(f'Exported {table_name} to {filename}'))
