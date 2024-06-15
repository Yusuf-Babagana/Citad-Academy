# payments/views.py
from django.shortcuts import render
from django.shortcuts import redirect, HttpResponse
from django.conf import settings
from paystackapi.transaction import Transaction
import uuid  # for generating a unique reference
from .models import Payment
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from paystackapi.paystack import Paystack
from user_management.models import User
from django.contrib.auth.decorators import login_required
from .payments import paystack_conn  # Import the Paystack connection
from django.contrib.auth import get_user_model
from subscription.models import Subscription
from django.shortcuts import get_object_or_404

def initialize_transaction(request):
    unique_reference = str(uuid.uuid4())
    customer_email = request.user.email
    role = request.user.role  # Assuming 'role' is an attribute of your user model
    
    # Set payment amount based on role
    if role == 'SA':
        amount_in_kobo = 2000000  # 20,000 Naira for School Admins (in kobo)
    elif role == 'T':
        amount_in_kobo = 0  # Teachers might not pay
    elif role == 'S':
        amount_in_kobo = 200000  # 2,000 Naira for Students (in kobo)
    elif role == 'IL':
        amount_in_kobo = 200000  # 2,000 Naira for Independent Learners (in kobo)
    else:
        return HttpResponse("Invalid user role.")
    
    # Save payment info to the database
    term_end_date = timezone.now() + timedelta(days=365)
    new_payment = Payment(
        user=request.user, 
        reference=unique_reference, 
        amount=amount_in_kobo, 
        status='initialized',
        payment_type='termly',
        term_end_date=term_end_date
    )
    new_payment.save()

    # Initialize the Paystack transaction
    response = Transaction.initialize(
        reference=unique_reference,
        amount=amount_in_kobo,
        email=customer_email
    )
    authorization_url = response['data']['authorization_url']
    return redirect(authorization_url)

User = get_user_model()  # Get the custom user model

@login_required
def verify_transaction(request):
    reference = request.GET.get('reference')  # Get reference from query parameters
    if not reference:
        return JsonResponse({"status": "error", "message": "No reference provided."}, status=400)
    
    payment = get_object_or_404(Payment, reference=reference, user=request.user)
    response = Transaction.verify(reference=reference)

    if response['status'] == True and response['data']['status'] == 'success':
        payment.status = 'completed'
        payment.save()

        # Directly create a new subscription for the user based on payment details
        subscription = Subscription.objects.create(
            user=request.user,
            name=f"{request.user.get_role_display()} Subscription",  # Custom name based on user role
            start_date=timezone.now(),  # Set the start date to now
            end_date=timezone.now() + timedelta(days=365),  # Set end date based on your duration logic
            duration=365,  # Example fixed duration, customize as needed
            cost=payment.amount / 100,  # Assuming cost is in Naira
            status='active',  # Immediately set to active
        )
        payment.subscription = subscription  # Link the new subscription to the payment
        payment.save()

        return JsonResponse({"status": "success", "message": "Payment successful and subscription activated."})
    else:
        return JsonResponse({"status": "error", "message": "Payment verification failed."}, status=400)

    
def payment_page(request):
    user = request.user
    role = user.role 

    context = {
        'role': role,
    }

    return render(request, 'payment_page.html', context)

def initialize_payment_for_subscription(request, subscription):
    unique_reference = str(uuid.uuid4())
    customer_email = request.user.email
    amount_in_kobo = subscription.cost * 100  # Assuming cost is in Naira

    # Create a Payment record linked to the subscription
    new_payment = Payment.objects.create(
        user=request.user,
        subscription=subscription,
        reference=unique_reference,
        amount=amount_in_kobo,
        status='initialized',
        payment_type='subscription',
        # term_end_date is calculated based on the subscription duration
    )

    # Initialize Paystack transaction
    response = Transaction.initialize(reference=unique_reference, amount=amount_in_kobo, email=customer_email)
    authorization_url = response['data']['authorization_url']
    return redirect(authorization_url)