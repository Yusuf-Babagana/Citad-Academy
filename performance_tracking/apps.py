from django.apps import AppConfig

class PerformanceTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'performance_tracking'

    def ready(self):
        # Import and connect the signals
        from . import signals
