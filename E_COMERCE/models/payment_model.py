from django.db import models
from E_COMERCE.models import Order
from E_COMERCE.constants.default_values import PaymentStatus

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(
        choices=[(ps.value, ps.name) for ps in PaymentStatus],
        default=PaymentStatus.PENDING.value,
    )
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    payment_gateway_order_id = models.CharField(max_length=100, blank=True, null=True)
    utr = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paments'

    def __str__(self):
        return f"Payment {self.id} for Order {self.order_id} [{self.status}]"
