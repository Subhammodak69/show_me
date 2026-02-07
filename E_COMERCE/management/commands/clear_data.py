from django.core.management.base import BaseCommand
from E_COMERCE.models import *

class Command(BaseCommand):
    help = 'Clear all application data (Render safe)'

    def handle(self, *args, **options):        
        print("🗑️  Deleting all data...")
        
        # Delete in SAFE order (avoids foreign key errors)
        
        # Poster.objects.all().delete()
        # Category.objects.all().delete()
        # SubCategory.objects.all().delete()
        # Product.objects.all().delete()
        # ProductItem.objects.all().delete()
        # Rating.objects.all().delete()

        # Wishlist.objects.all().delete()
        # Cart.objects.all().delete()
        # Order.objects.all().delete()
        # OrderItem.objects.all().delete()
        # CartItem.objects.all().delete()

        user = User.objects.filter(username = 'modaksubham69@gmail.com').first()
        print(user.email,user.password)      
        
        print("✅ ALL DATA DELETED SUCCESSFULLY!")
        self.stdout.write(self.style.SUCCESS('Database cleared!'))
