from django.db import models 
from E_COMERCE.models import User
from E_COMERCE.models.productitem_model import ProductItem
class Wishlist(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wishlists')
    product_item = models.ForeignKey(ProductItem,on_delete=models.CASCADE,related_name='wishlists')

    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wishlists'

    def __str__(self):
        return f"ID: {self.id} created_at: {self.created_at} is_active: {self.is_active}"


