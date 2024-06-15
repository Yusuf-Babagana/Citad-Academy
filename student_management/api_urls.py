from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.StudentList.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetail.as_view(), name='student-detail'),
    path('enrollments/', views.EnrollmentRequestList.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', views.EnrollmentRequestDetail.as_view(), name='enrollment-detail'),
]


from django.urls import path
from .api_views import (
    StudentListView, StudentDetailView, StudentExamListView, StudentExamDetailView,
    EnrollmentRequestListView, EnrollmentRequestDetailView, SubjectCombinationListView,
    SubjectCombinationDetailView, StudentPerformanceListView, StudentPerformanceDetailView,
    StudentActivityListView, StudentActivityDetailView, BehavioralAssessmentListView,
    BehavioralAssessmentDetailView
)

urlpatterns = [
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('student-exams/', StudentExamListView.as_view(), name='student-exam-list'),
    path('student-exams/<int:pk>/', StudentExamDetailView.as_view(), name='student-exam-detail'),
    path('enrollment-requests/', EnrollmentRequestListView.as_view(), name='enrollment-request-list'),
    path('enrollment-requests/<int:pk>/', EnrollmentRequestDetailView.as_view(), name='enrollment-request-detail'),
    path('subject-combinations/', SubjectCombinationListView.as_view(), name='subject-combination-list'),
    path('subject-combinations/<int:pk>/', SubjectCombinationDetailView.as_view(), name='subject-combination-detail'),
    path('student-performances/', StudentPerformanceListView.as_view(), name='student-performance-list'),
    path('student-performances/<int:pk>/', StudentPerformanceDetailView.as_view(), name='student-performance-detail'),
    path('student-activities/', StudentActivityListView.as_view(), name='student-activity-list'),
    path('student-activities/<int:pk>/', StudentActivityDetailView.as_view(), name='student-activity-detail'),
    path('behavioral-assessments/', BehavioralAssessmentListView.as_view(), name='behavioral-assessment-list'),
    path('behavioral-assessments/<int:pk>/', BehavioralAssessmentDetailView.as_view(), name='behavioral-assessment-detail'),
]
