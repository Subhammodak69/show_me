from django.contrib.auth.models import AbstractUser
from django.db import models
from ..constants.default_values import Gender,Role

class User(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    profile_photo_url = models.URLField(blank=True, null=True)
    
    gender = models.IntegerField(
        choices=[(gender.value, gender.name) for gender in Gender],
        default=Gender.MALE.value,
        null=False,
        blank=False
    )
    address = models.TextField(max_length=255, null=True , blank= True )
    role = models.IntegerField(
        choices=[(role.name,role.value) for role in Role],
        default=Role.ENDUSER.value,
        blank=False,
        null = False
    )
    phone = models.CharField(max_length=12,blank=True,null=True)
    email = models.EmailField(max_length=100, blank=False, null=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'users'
    def __str__(self):
        return f"ID:{self.id} Is_active:{self.is_active} Created_at:{self.created_at}"
