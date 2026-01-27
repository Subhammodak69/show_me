from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from E_COMERCE.models import ProductItem, Rating, Poster, Category, Product, User

class Command(BaseCommand):
    help = 'Clear all application data (Render safe)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        print("🗑️  Deleting all data...")
        
        # Delete in SAFE order (avoids foreign key errors)
        ProductItem.objects.all().delete()
        Rating.objects.all().delete()
        Poster.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
        
        print("✅ ALL DATA DELETED SUCCESSFULLY!")
        self.stdout.write(self.style.SUCCESS('Database cleared!'))
