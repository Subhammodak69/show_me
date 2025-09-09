from django.db import models
from E_COMERCE.models import User
from E_COMERCE.constants.default_values import PayMethods,PaymentStatus,Banks

class Payment(models.Model):
    method = models.IntegerField(
        choices=[(m.value,m.name) for m in PayMethods],
        blank=False,
        null=False
    )

    status = models.IntegerField(
        choices=[(s.value,s.name) for s in PaymentStatus],
        blank=False,
        null=False
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    card_number = models.CharField(max_length=19, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    bank = models.IntegerField(
        choices=[(b.value,b.name) for b in Banks],
        blank=True,  # Fixed: Allow blank
        null=True    # Fixed: Allow null
    )

    class Meta:
        db_table = 'payments'
        
    def __str__(self):
        return f"Payment {self.id} by {self.user} - {self.status}"
