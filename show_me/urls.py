from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('', include('E_COMERCE.urls')),  # Pass the string path to the module
]
