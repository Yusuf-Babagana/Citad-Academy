#media_management/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaViewSet, index
from . import views

router = DefaultRouter()
router.register(r'media', MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('index/', index, name='index'),  # new URL pattern
    path('upload/', views.upload_media, name='media_upload'),
    path('view_media/<int:media_id>/', views.view_media, name='view_media'),
    path('categories/', views.list_category_types, name='list_category_types'),
    path('categories/<int:category_type_id>/details/', views.list_category_details, name='list_category_details'),
    path('details/<int:category_detail_id>/media/', views.list_media_files, name='list_media_files'),
]
