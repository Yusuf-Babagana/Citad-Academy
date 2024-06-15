from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.LeaderboardList.as_view(), name='leaderboard-list'),
    path('leaderboard/<int:pk>/', views.LeaderboardDetail.as_view(), name='leaderboard-detail'),
]


from django.urls import path
from .api_views import LeaderboardListView, LeaderboardDetailView

urlpatterns = [
    path('leaderboards/', LeaderboardListView.as_view(), name='leaderboard-list'),
    path('leaderboards/<int:pk>/', LeaderboardDetailView.as_view(), name='leaderboard-detail'),
]
