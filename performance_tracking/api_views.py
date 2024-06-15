from rest_framework import generics
from .models import Performance, AttendanceRecord, ExtraCurricularActivity, ReportCard
from .serializers import PerformanceSerializer, AttendanceRecordSerializer, ExtraCurricularActivitySerializer, ReportCardSerializer
from rest_framework.permissions import IsAuthenticated

class PerformanceListView(generics.ListCreateAPIView):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticated]

class AttendanceRecordListView(generics.ListCreateAPIView):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]

class ExtraCurricularActivityListView(generics.ListCreateAPIView):
    queryset = ExtraCurricularActivity.objects.all()
    serializer_class = ExtraCurricularActivitySerializer
    permission_classes = [IsAuthenticated]

class ReportCardDetailView(generics.RetrieveUpdateAPIView):
    queryset = ReportCard.objects.all()
    serializer_class = ReportCardSerializer
    permission_classes = [IsAuthenticated]
