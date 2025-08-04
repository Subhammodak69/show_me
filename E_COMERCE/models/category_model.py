from django.db import models
from E_COMERCE.models import User


class Category(models.Model):
    name = models.CharField(max_length=250, blank= False, null = False)
    description = models.TextField(blank=False, null=False)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE , related_name='categories')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return f"ID: {self.id} Created_at: {self.created_at} is_active: {self.is_active}"

