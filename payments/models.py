# payments/models.py
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
# Ensure to adjust this import to avoid circular dependencies
from subscription.models import Subscription  

PAYMENT_TYPES = [
    ('termly', 'Termly Payment'),
]

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')  # Add this line
    reference = models.CharField(max_length=100)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(choices=PAYMENT_TYPES, max_length=20, default='termly')
    term_end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id and self.subscription:  # Check if this is a new instance and subscription is set
            # Adjust term_end_date based on the subscription's duration
            self.term_end_date = timezone.now() + timedelta(days=self.subscription.duration)
        super(Payment, self).save(*args, **kwargs)