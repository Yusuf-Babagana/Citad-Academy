# class_management/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('classes/', api_views.ClassListView.as_view(), name='class-list'),
    path('teachers/', api_views.TeacherListView.as_view(), name='teacher-list'),
    path('subjects/', api_views.SubjectListView.as_view(), name='subject-list'),
]

