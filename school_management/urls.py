# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('schools/', views.SchoolList.as_view(), name='school-list'),
    path('schools/<int:pk>/', views.SchoolDetail.as_view(), name='school-detail'),
    path('', views.index, name='index'),  # new URL pattern
]
