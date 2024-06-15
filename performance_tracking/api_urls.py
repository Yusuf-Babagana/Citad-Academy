from django.urls import path
from . import views

urlpatterns = [
    
]


from django.urls import path
from .api_views import (
    PerformanceListView, AttendanceRecordListView, ExtraCurricularActivityListView, ReportCardDetailView
)

urlpatterns = [
    path('performance/', PerformanceListView.as_view(), name='performance-list'),
    path('attendance/', AttendanceRecordListView.as_view(), name='attendance-list'),
    path('extra-curricular/', ExtraCurricularActivityListView.as_view(), name='extra-curricular-list'),
    path('report-card/<int:pk>/', ReportCardDetailView.as_view(), name='report-card-detail'),
]
