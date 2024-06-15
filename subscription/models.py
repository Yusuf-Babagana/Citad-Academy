#subscription/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver

def get_default_user():
    User = get_user_model()
    default_email = 'default@example.com'
    default_username = 'default_user'
    default_role = 'A'  # Assuming 'A' is a valid role in your ROLE_CHOICES

    # Attempt to get or create the default user
    user, created = User.objects.get_or_create(
        username=default_username, defaults={
            'email': default_email,
            'role': default_role,
            # default
        }
    )

    return user.id

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', default=get_default_user)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=True, blank=True)  # Allow null until activation
    end_date = models.DateTimeField(null=True, blank=True)  # Allow null until set based on duration
    duration = models.IntegerField(help_text="Duration in days")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    long_term_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="In percentage")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Start as 'pending'

    def __str__(self):
        return f"{self.user.username if self.user else 'Default User'} - {self.name}"

    def is_subscription_active(self):
        # Check that the subscription is active and the end date is in the future
        return self.status == 'active' and self.end_date and timezone.now() <= self.end_date

    def activate(self, duration_days=None):
        """Activates the subscription, setting start and end dates based on the provided duration or self.duration."""
        self.start_date = timezone.now()
        self.end_date = self.start_date + timezone.timedelta(days=duration_days or self.duration)
        self.status = 'active'
        self.save()

# Adjusting the model to ensure a default user is set before saving, if none is provided
@receiver(pre_save, sender=Subscription)
def set_default_user(sender, instance, **kwargs):
    if not instance.user:
        instance.user = get_default_user()

class BulkDiscount(models.Model):
    min_subscriptions = models.IntegerField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # In percentage

    def __str__(self):
        return f"{self.min_subscriptions} - {self.discount}%"

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # In percentage
    expiry_date = models.DateField(null=True, blank=True)
    usage_limit = models.IntegerField(default=1)  # Number of times it can be used
    subscription = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL)  # Optional

    def __str__(self):
        return self.code
