from django.db import models
from E_COMERCE.models import ProductItem 

class ProductImage(models.Model):
    product_item = models.ForeignKey(
        ProductItem, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    photo_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_images'
    
    def __str__(self):
        return f"ID: {self.id}, Is_active: {self.is_active}" 
