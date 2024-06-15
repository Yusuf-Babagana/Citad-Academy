#school_management app
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)  # New field for the school logo
    description = models.TextField(null=True, blank=True)  # Optional field for school description

    def __str__(self):
        return self.name

class SchoolAdmin(models.Model):
    user = models.OneToOneField('user_management.User', on_delete=models.CASCADE, related_name='school_admin')
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='admin')

    def __str__(self):
        return self.user.username
