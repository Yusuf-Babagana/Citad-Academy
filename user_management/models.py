# user_management/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from subscription.models import Subscription

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SA', 'School Admin'),
        ('T', 'Teacher'),
        ('S', 'Student'),
        ('A', 'Admin'),
        ('IL', 'Independent Learner'),  # Adding the Independent Learner role
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    school = models.ForeignKey('school_management.School', on_delete=models.SET_NULL, null=True, blank=True)
    subscription = models.ForeignKey('subscription.Subscription', null=True, blank=True, on_delete=models.SET_NULL, related_name='current_subscription_of_user')
    subscription_expiry_date = models.DateField(null=True, blank=True)
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    has_paid_subscription = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='user_profiles/', null=True, blank=True, verbose_name='Profile Image')

    def __str__(self):
        return self.username