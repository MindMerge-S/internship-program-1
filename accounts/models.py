from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    image = models.ImageField(default='profile/defaultProfile.png')
    def __str__(self):
        return f'{self.user.username} Profile'