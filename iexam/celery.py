#iexam/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iexam.settings')

app = Celery('iexam')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' is optional, but it allows you to have all Celery-related configuration keys in Django settings
#   prefixed with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_for_expiring_subscriptions': {
        'task': 'subscription.tasks.check_for_expiring_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Executes every day at midnight
    },
    'update_subscription_status': {
        'task': 'subscription.tasks.update_subscription_status',
        'schedule': crontab(hour=0, minute=10),  # Executes every day 10 minutes past midnight
    },
    # You can add more periodic task schedules here
}
