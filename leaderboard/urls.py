from django.urls import path
from .views import independent_leaderboard, school_leaderboard
from . import views

urlpatterns = [
    path('leaderboard/', views.LeaderboardList.as_view(), name='leaderboard-list'),
    path('leaderboard/<int:pk>/', views.LeaderboardDetail.as_view(), name='leaderboard-detail'),
    path('', views.index, name='index'),
    path('class/<int:class_id>/leaderboard/', views.class_leaderboard, name='class-leaderboard'),  # new URL pattern
    path('subject/<int:subject_id>/leaderboard/', views.subject_leaderboard, name='subject-leaderboard'),  # new URL pattern
    path('leaderboard/independent/<int:subject_id>/', independent_leaderboard, name='independent_leaderboard'),
    path('leaderboard/schools/', school_leaderboard, name='school_leaderboard'),
]
