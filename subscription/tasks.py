# subscription/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from user_management.models import User  # make sure to import the User model
from .utils import send_renewal_email  # assuming this is correctly implemented

@shared_task
def check_for_expiring_subscriptions():
    # Find users whose subscription is about to expire
    soon_to_expire_users = User.objects.filter(
        subscription_expiry_date__lte=timezone.now().date() + timedelta(days=3),
        subscription_expiry_date__gt=timezone.now().date(),
        has_paid_subscription=True
    )
    for user in soon_to_expire_users:
        send_renewal_email(user)

@shared_task
def update_subscription_status():
    # Find users whose trial has expired and set is_on_trial to False
    users_with_expired_trial = User.objects.filter(
        trial_end_date__lt=timezone.now(),
        trial_start_date__isnull=False  # Only consider users with a trial start date
    )
    for user in users_with_expired_trial:
        user.is_on_trial = False
        user.save(update_fields=['is_on_trial'])

    # Find users whose subscription has expired and set has_paid_subscription to False
    expired_subscriptions = User.objects.filter(
        subscription_expiry_date__lt=timezone.now().date(),
        has_paid_subscription=True
    )
    for user in expired_subscriptions:
        user.has_paid_subscription = False
        user.save(update_fields=['has_paid_subscription'])

    # Any additional logic for sending notifications or updates
