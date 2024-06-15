# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.SubjectList.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetail.as_view(), name='subject-detail'),
    path('topics/', views.TopicList.as_view(), name='topic-list'),
    path('topics/<int:pk>/', views.TopicDetail.as_view(), name='topic-detail'),
    path('', views.index, name='index'),  # new URL pattern
]
