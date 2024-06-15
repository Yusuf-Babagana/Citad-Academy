from django.urls import path
from . import views

app_name = 'resource'

urlpatterns = [
    path('', views.ResourceListView.as_view(), name='resource_list'),
    path('<slug:slug>/', views.ResourceDetailView.as_view(), name='resource_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('<slug:slug>/download/', views.download_resource, name='download_resource'),

]
