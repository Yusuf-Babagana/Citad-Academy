from django.urls import path
from . import views
from .views import (
    StudentPerformanceCreateView,
    StudentPerformanceUpdateView,
    StudentActivityCreateView,
    StudentActivityUpdateView,
    BehavioralAssessmentCreateView,
    BehavioralAssessmentUpdateView,
)


urlpatterns = [
    path('students/', views.StudentList.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetail.as_view(), name='student-detail'),
    path('enrollments/', views.EnrollmentRequestList.as_view(), name='enrollment-request-list'),
    path('enrollments/<int:pk>/', views.EnrollmentRequestDetail.as_view(), name='enrollment-request-detail'),
    path('subject_selection/', views.SubjectSelectionView.as_view(), name='subject-selection'),  # New URL
    path('', views.index, name='index'),
    path('student/performance/create/', StudentPerformanceCreateView.as_view(), name='student_performance_create'),
    path('student/performance/<int:pk>/update/', StudentPerformanceUpdateView.as_view(), name='student_performance_update'),
    path('student/activity/create/', StudentActivityCreateView.as_view(), name='student_activity_create'),
    path('student/activity/<int:pk>/update/', StudentActivityUpdateView.as_view(), name='student_activity_update'),
    path('student/assessment/create/', BehavioralAssessmentCreateView.as_view(), name='behavioral_assessment_create'),
    path('student/assessment/<int:pk>/update/', BehavioralAssessmentUpdateView.as_view(), name='behavioral_assessment_update'),
]
