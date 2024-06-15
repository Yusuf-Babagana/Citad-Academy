from rest_framework import generics
from .models import Subscription, BulkDiscount, Coupon
from .serializers import SubscriptionSerializer, BulkDiscountSerializer, CouponSerializer
from rest_framework.permissions import IsAuthenticated

class SubscriptionListView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

class BulkDiscountListView(generics.ListCreateAPIView):
    queryset = BulkDiscount.objects.all()
    serializer_class = BulkDiscountSerializer
    permission_classes = [IsAuthenticated]

class CouponListView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
