from django.urls import path
from .api_views import PaymentListView, PaymentDetailView

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
]

