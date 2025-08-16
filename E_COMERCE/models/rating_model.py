from django.db import models
from E_COMERCE.models import Product,User

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    photo_url = models.URLField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    review = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')  # each user can rate each product once
        db_table = 'product_ratings'

    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.rating} stars"
