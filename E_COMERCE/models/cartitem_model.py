from django.db import models
from E_COMERCE.models import ProductItem,Cart 
from E_COMERCE.constants.default_values import Size,Color 

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='cart_items')
    size = models.IntegerField(choices=[(s.value, s.name) for s in Size])
    quantity = models.PositiveIntegerField(default=1)
    color = models.IntegerField(choices=[(c.value, c.name) for c in Color])

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product_item', 'size')  # optional: avoid duplicates for same product-size

    def __str__(self):
        return f"{self.product_item} (x{self.quantity}) in Cart {self.cart.id}"