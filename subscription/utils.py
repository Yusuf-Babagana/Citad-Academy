#subscription/utils.py
from django.core.mail import send_mail
from django.conf import settings
from user_management.models import User
from django.contrib.auth.decorators import login_required 
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect

def send_renewal_email(user):
    subject = 'Your subscription is expiring soon!'
    message = f'Dear {user.username},\n\nYour subscription will expire soon. Please renew it to continue enjoying our services.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email,]

    send_mail(subject, message, email_from, recipient_list)

def check_user_access(user):
    now = timezone.now()
    if user.is_on_trial and user.trial_end_date >= now:
        return True
    if user.subscription_expiry_date and user.subscription_expiry_date >= now.date():
        return True
    return False

@login_required  # Ensures that the user must be logged in
def some_protected_view(request):
    if not check_user_access(request.user):
        # Redirect to the subscription page or show a message
        return redirect('payment_page')
    # Your protected view logic here