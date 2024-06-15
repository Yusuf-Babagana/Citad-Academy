from django.urls import path
from .api_views import (
    SubscriptionListView, SubscriptionDetailView, BulkDiscountListView, CouponListView, CouponDetailView
)

urlpatterns = [
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('bulk-discounts/', BulkDiscountListView.as_view(), name='bulk-discount-list'),
    path('coupons/', CouponListView.as_view(), name='coupon-list'),
    path('coupons/<int:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
]
