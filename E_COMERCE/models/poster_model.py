from django.db import models
from E_COMERCE.models import User

class Poster(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posters')
    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=False, null=False)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posters'

    def __str__(self):
        return f"Poster by {self.created_by.id} - {self.title or 'No Title'} (Active: {self.is_active})"
