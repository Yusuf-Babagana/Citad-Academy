from django.urls import path
from . import api_views
from .api_views import SchoolUpdateAPIView

urlpatterns = [
    path('schools/', api_views.SchoolListView.as_view(), name='school-list'),
    path('schools/<int:pk>/', api_views.SchoolDetailView.as_view(), name='school-detail'),
    path('school-admins/', api_views.SchoolAdminView.as_view(), name='school-admin-list'),
    path('school/<int:pk>/update/', SchoolUpdateAPIView.as_view(), name='school-update'),
]
