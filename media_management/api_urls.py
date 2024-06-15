from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaViewSet

router = DefaultRouter()
router.register(r'media', MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


from django.urls import path
from .api_views import (
    CategoryTypeListView, CategoryDetailListView, MediaListView, MediaDetailView, CommentListView, CommentDetailView
)

urlpatterns = [
    path('category-types/', CategoryTypeListView.as_view(), name='category-type-list'),
    path('category-details/', CategoryDetailListView.as_view(), name='category-detail-list'),
    path('media/', MediaListView.as_view(), name='media-list'),
    path('media/<int:pk>/', MediaDetailView.as_view(), name='media-detail'),
    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
