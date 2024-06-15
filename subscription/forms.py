# subscription/forms.py

from django import forms
from .models import Subscription

class SubscriptionSelectionForm(forms.Form):
    subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.none(),
        label="Choose your subscription plan",
        required=True,
        empty_label="Select a plan"
    )

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        super().__init__(*args, **kwargs)
        if user_role:
            # Adjusting to check for descriptive names in the subscription plans
            self.fields['subscription'].queryset = Subscription.objects.filter(
                name__icontains=user_role,  # Look for a match within the subscription name
                status='active'  # Only active subscriptions
            )
            print(f"Available subscriptions for {user_role}: {self.fields['subscription'].queryset.count()}")

            
