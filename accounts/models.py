from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('traveler', 'Traveler'),
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='traveler')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

class VendorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)

class TravelerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    travel_history = models.TextField(blank=True)