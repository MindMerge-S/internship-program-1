from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RegistrationOTP(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=255)

    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    image = models.ImageField(default='profile/defaultProfile.png')
    def __str__(self):
        return f'{self.user.username} Profile'