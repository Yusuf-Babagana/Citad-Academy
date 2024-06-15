from django.urls import path
from .views import ClassList, ClassDetail, ClassCreateView, SubjectCreateView, index

app_name = 'class_management'

urlpatterns = [
    path('classes/', ClassList.as_view(), name='class-list'),
    path('classes/<int:pk>/', ClassDetail.as_view(), name='class-detail'),
    path('create_class/', ClassCreateView.as_view(), name='create-class'),
    path('create_subject/', SubjectCreateView.as_view(), name='create-subject'),
    path('', index, name='index'),
]
