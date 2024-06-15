# payments/urls.py

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initialize_transaction/', views.initialize_transaction, name='initialize_transaction'),
    path('verify_transaction/', views.verify_transaction, name='verify_transaction'),  # This is correct for query parameters
    path('payment_page/', views.payment_page, name='payment_page'),
]
