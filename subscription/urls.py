#subscription/urls.py
from django.urls import path
from . import views
from .views import renew_subscription, subscription_detail, select_subscription


app_name = 'subscription'

urlpatterns = [
   
    path('list/', views.list_subscriptions, name='list_subscriptions'),
    path('detail/<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('renew/<int:pk>/', views.renew_subscription, name='renew_subscription'),
    path('initiate/', views.initiate_subscription, name='initiate_subscription'),
    path('select/', select_subscription, name='select_subscription'),


]
