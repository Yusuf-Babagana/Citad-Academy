from rest_framework import serializers
from .models import Subscription, BulkDiscount, Coupon

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'name', 'start_date', 'end_date', 'duration', 'cost', 'long_term_discount', 'status']

class BulkDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkDiscount
        fields = ['id', 'min_subscriptions', 'discount']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount', 'expiry_date', 'usage_limit', 'subscription']
