from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'subscription', 'reference', 'amount', 'status', 'created_at', 'payment_type', 'term_end_date']
