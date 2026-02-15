from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync ALL project models from default (Render) → local DB'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview only')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Test local connection
        try:
            connections['local'].ensure_connection()
            self.stdout.write(self.style.SUCCESS('✅ Local DB connected'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Local DB unavailable: {e}'))
            return
        
        # Get ALL models from ALL apps in your project
        total_synced = 0
        models_synced = []
        
        for model in apps.get_models():
            try:
                model_name = f"{model._meta.app_label}.{model._meta.model_name}"
                
                # Skip auth/contenttypes (system models)
                if model._meta.app_label in ['auth', 'contenttypes', 'admin', 'sessions']:
                    continue
                
                # Fetch from Render DB (default)
                render_data = list(model.objects.using('default').values())
                
                if render_data:
                    if dry_run:
                        self.stdout.write(f"📋 {model_name}: {len(render_data)} records")
                    else:
                        # Clear local data
                        model.objects.using('local').all().delete()
                        
                        # Sync to local
                        local_objects = [model(**data) for data in render_data]
                        model.objects.using('local').bulk_create(local_objects, ignore_conflicts=True)
                        
                        total_synced += len(render_data)
                        models_synced.append(f"{model_name} ({len(render_data)})")
                        
                        self.stdout.write(self.style.SUCCESS(f"✅ {model_name}: {len(render_data)} records"))
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  {model_name}: {e}"))
                continue
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n🎉 SYNC COMPLETE!"))
        self.stdout.write(f"📊 Total records: {total_synced}")
        self.stdout.write(f"📋 Models: {', '.join(models_synced[:5])}" + 
                         (f", +{len(models_synced)-5} more" if len(models_synced) > 5 else ""))
