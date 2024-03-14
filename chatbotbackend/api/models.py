from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True, default = '03086955656')
    date_of_birth = models.DateField(blank=True, null=True, default = '')
    address = models.TextField(blank=True, null=True, default = '')
    status = models.TextField(blank=True, null=True, default = 'Offline')
    # profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default = '')
    # Add more fields as needed

    def __str__(self):
        return self.user.username
