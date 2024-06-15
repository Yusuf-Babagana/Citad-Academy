from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.SubjectList.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetail.as_view(), name='subject-detail'),
    path('topics/', views.TopicList.as_view(), name='topic-list'),
    path('topics/<int:pk>/', views.TopicDetail.as_view(), name='topic-detail'),
]


from django.urls import path
from . import api_views

urlpatterns = [
    path('topics/', api_views.TopicListView.as_view(), name='topic-list'),
    path('subtopics/', api_views.SubTopicListView.as_view(), name='subtopic-list'),
]
