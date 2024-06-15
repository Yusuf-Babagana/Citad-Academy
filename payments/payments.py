# payments/payments.py

from django.conf import settings
from paystackapi.paystack import Paystack

paystack_conn = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
