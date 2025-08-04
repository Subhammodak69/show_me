from django.db import models
from E_COMERCE.models.sub_category_model import SubCategory

class Product(models.Model):
    name = models.CharField(max_length=250, blank= False, null = False)
    description = models.TextField(blank=False, null=False)
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name='products')


    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"ID: {self.id} Created_at: {self.created_at} is_active: {self.is_active}"

