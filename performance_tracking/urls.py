# performance_tracking/urls.py
from django.urls import path
from .views import individual_student_report, calculate_overall_performance, view_academic_performance, view_activities_score, view_behavioral_score
from . import views

urlpatterns = [
    path('performance/overall/<int:student_id>/<int:subject_id>/<str:term>/<int:year>/', calculate_overall_performance, name='overall_performance'),
    path('performance/academic/<int:student_id>/<int:subject_id>/', view_academic_performance, name='academic_performance'),
    path('performance/activities/<int:student_id>/', view_activities_score, name='activities_score'),
    path('performance/behavioral/<int:student_id>/', view_behavioral_score, name='behavioral_score'),
    path('performance/student/<int:student_id>/report/', individual_student_report, name='individual_student_report'),
    path('student-report/<int:student_id>/', views.individual_student_report, name='individual_student_report'),
    path('report-card/<int:student_id>/', views.generate_report_card_view, name='generate_report_card_view'),
]
