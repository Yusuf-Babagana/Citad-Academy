# subscription/check_subscription_middleware.py
from django.utils.timezone import now
from django.utils import timezone
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from subscription.models import Subscription
from django.conf import settings
from user_management.models import User  # Make sure to import User

class CheckUserSubscription(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip checks for non-authenticated users or specific bypass paths
        if not request.user.is_authenticated or self.should_bypass(request):
            return self.get_response(request)

        # Check if the user is within their trial period and allow access
        if self.is_in_trial_period(request.user):
            return self.get_response(request)

        # Allow teachers to always have access, no subscription check needed
        if request.user.role == 'T':
            return self.get_response(request)

        # Redirect users without an active subscription to the subscription selection page
        if self.requires_subscription_check(request) and not self.has_active_subscription(request.user):
            return redirect('subscription:select_subscription')

        return self.get_response(request)

    def should_bypass(self, request):
        allowed_paths = self.build_allowed_paths()
        return request.path in allowed_paths or 'verify_transaction' in request.path

    def build_allowed_paths(self):
        allowed_paths = [
            reverse('user_management:index'),
            reverse('resource:resource_list'),
            reverse('user_management:logout'),
            reverse('user_management:get_started'),
            reverse('user_management:take_tour'),
            reverse('user_management:video_tour'),
            reverse('resource:contact'),
            reverse('payments:initialize_transaction'),
            reverse('payments:payment_page'),
            reverse('admin:index'),
            reverse('admin:login'),
            '/ckeditor/upload/',
            reverse('subscription:select_subscription'),
            reverse('payments:verify_transaction'),
        ]
        return allowed_paths

    def requires_subscription_check(self, request):
        subscription_required_paths = {
            reverse('user_management:school-admin-dashboard'),
            reverse('user_management:student-dashboard'),
            reverse('user_management:independent_learner_dashboard'),
        }
        return request.path in subscription_required_paths

    def has_active_subscription(self, user):
        return Subscription.objects.filter(user=user, status='active', end_date__gte=now()).exists()

    def is_in_trial_period(self, user):
        """Check if the user is within their trial period."""
        # Ensure both trial_start_date and trial_end_date are not None before comparison
        if user.trial_start_date and user.trial_end_date:
            return user.trial_start_date <= timezone.now() <= user.trial_end_date
        return False