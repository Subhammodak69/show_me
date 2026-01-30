from django.db import models
from E_COMERCE.models import ProductItem,Order
from E_COMERCE.constants.default_values import Size,Color

class OrderItem(models.Model):
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='orderitems')
    order_id = models.ForeignKey(Order,on_delete= models.CASCADE , related_name='orderitems')
    quantity = models.IntegerField(blank=False,null=False,default= 1)
    size = models.IntegerField(
        choices=[(s.value, s.name) for s in Size],
        blank=False,
        null=False
    )
    color = models.IntegerField(
        choices=[(c.value, c.name) for c in Color],
        blank=False,
        null=False
    )
    price = models.IntegerField(blank= False,null=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orderitems'

    def __str__(self):
        return f"ID: {self.id} Created_at: {self.created_at} Is_active: {self.is_active}"
    
    