# subscription/views.py
from django.shortcuts import render, redirect, HttpResponse
from .models import Subscription
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Subscription
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from payments.views import initialize_payment_for_subscription
from django.contrib import messages
from .forms import SubscriptionSelectionForm


@login_required
def list_subscriptions(request):
    # Assuming each role has specific subscription types, you might want to filter subscriptions by a criterion that matches the user's role.
    # This example directly fetches subscriptions linked to the user, assuming they are relevant to their role.
    subscription = Subscription.objects.filter(user=request.user)
    return render(request, 'subscription/list_subscriptions.html', {'subscription': subscription})

@login_required
def subscription_detail(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    return render(request, 'subscription/subscription_detail.html', {'subscription': subscription})

@login_required
def renew_subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)

    if request.method == 'POST':
        subscription.end_date += timedelta(days=365)  # Extend the subscription for another year
        subscription.status = 'active'  # Ensure the subscription is active
        subscription.save()

        messages.success(request, 'Your subscription has been successfully renewed.')
        return redirect('subscription:subscription_detail', pk=subscription.pk)
    else:
        # If GET request, show confirmation page
        return render(request, 'subscription/renew_subscription_confirm.html', {'subscription': subscription})

def determine_subscription_for_user(user):
    role_subscription_map = {
        'SA': 'School Admin Subscription',
        'T': 'Teacher Subscription',
        'S': 'Student Subscription',
        'IL': 'Independent Learner Subscription',
    }
    subscription_name = role_subscription_map.get(user.role)
    print(f"Looking for subscription named: {subscription_name}")  # Debugging line
    
    subscription = Subscription.objects.filter(name=subscription_name).first()
    if subscription:
        print(f"Found subscription: {subscription.name}")  # Debugging line
    else:
        print("No subscription found for this role.")  # Debugging line
    
    return subscription

@login_required
def initiate_subscription(request):
    # Determine the appropriate subscription for the user based on their role
    # This is a placeholder function you'll need to implement
    subscription = determine_subscription_for_user(request.user)
    
    if subscription:
        # Redirect user to the payment process for the determined subscription
        return initialize_payment_for_subscription(request, subscription)
    else:
        # Handle cases where no subscription matches the user's role
        return HttpResponse("No suitable subscription found for your role.", status=404)

@login_required
def select_subscription(request):
    # Mapping short role codes to descriptive strings
    role_mapping = {
        'SA': 'School - Admin',
        'IL': 'Independent - Learner',
        'S': 'Student',
        # Add mappings for any other roles as necessary
    }

    # Get the descriptive role string based on the user's role
    user_role_descriptive = role_mapping.get(request.user.role, None)

    # Initialize the form with the descriptive role
    form = SubscriptionSelectionForm(user_role=user_role_descriptive)
    
    if request.method == 'POST':
        form = SubscriptionSelectionForm(request.POST, user_role=user_role_descriptive)
        if form.is_valid():
            subscription = form.cleaned_data['subscription']
            print(f"Selected subscription: {subscription.name}")
            # Proceed to payment view, passing the selected subscription instance
            return initialize_payment_for_subscription(request, subscription)
    
    return render(request, 'subscription/select_subscription.html', {'form': form})
