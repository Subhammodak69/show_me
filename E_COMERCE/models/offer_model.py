from django.db import models
from E_COMERCE.models import Product

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='offers')

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offers'

    def __str__(self):
        return f"{self.title} ({'active' if self.is_active else 'inactive'})"
