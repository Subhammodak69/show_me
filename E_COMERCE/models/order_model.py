from django.db import models
from E_COMERCE.models import User
from E_COMERCE.constants.default_values import Status

class Order(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.TextField(max_length=250)

    status = models.IntegerField(
        choices=[(s.value, s.name) for s in Status],
        default=Status.PENDING.value
    )
    total_price = models.IntegerField(blank=False, null=False)
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=12,blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"ID: {self.id} Created_at: {self.created_at} Is_active: {self.is_active}"

