from django.db import models
from E_COMERCE.models import Product
from E_COMERCE.constants.default_values import Size,Color

class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productitems')
    size = models.IntegerField(
        choices=[(s.name,s.value) for s in Size],
        blank=False,null=False
        )
    color = models.IntegerField(
        choices=[(c.name,c.value) for c in Color],
        blank=False,null=False
        )
    brand_name = models.CharField(max_length=200, null=True, blank=True)
    price = models.IntegerField(blank= False,null=False)
    photo_url = models.URLField(blank=False , null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    class Meta:
        db_table = 'productitems'

    def __str__(self):
        return f"ID: {self.id} Created_at: {self.created_at} is_active: {self.is_active}"
