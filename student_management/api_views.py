from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Student, StudentExam, EnrollmentRequest, SubjectCombination, StudentPerformance, StudentActivity, BehavioralAssessment
from .serializers import (
    StudentSerializer, StudentExamSerializer, EnrollmentRequestSerializer, 
    SubjectCombinationSerializer, StudentPerformanceSerializer, 
    StudentActivitySerializer, BehavioralAssessmentSerializer
)

# Example view for listing students
class StudentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentExamListView(generics.ListCreateAPIView):
    queryset = StudentExam.objects.all()
    serializer_class = StudentExamSerializer
    permission_classes = [IsAuthenticated]

class StudentExamDetailView(generics.RetrieveUpdateAPIView):
    queryset = StudentExam.objects.all()
    serializer_class = StudentExamSerializer
    permission_classes = [IsAuthenticated]

class EnrollmentRequestListView(generics.ListCreateAPIView):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

class EnrollmentRequestDetailView(generics.RetrieveUpdateAPIView):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

class SubjectCombinationListView(generics.ListCreateAPIView):
    queryset = SubjectCombination.objects.all()
    serializer_class = SubjectCombinationSerializer
    permission_classes = [IsAuthenticated]

class SubjectCombinationDetailView(generics.RetrieveUpdateAPIView):
    queryset = SubjectCombination.objects.all()
    serializer_class = SubjectCombinationSerializer
    permission_classes = [IsAuthenticated]

class StudentPerformanceListView(generics.ListCreateAPIView):
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    permission_classes = [IsAuthenticated]

class StudentPerformanceDetailView(generics.RetrieveUpdateAPIView):
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    permission_classes = [IsAuthenticated]

class StudentActivityListView(generics.ListCreateAPIView):
    queryset = StudentActivity.objects.all()
    serializer_class = StudentActivitySerializer
    permission_classes = [IsAuthenticated]

class StudentActivityDetailView(generics.RetrieveUpdateAPIView):
    queryset = StudentActivity.objects.all()
    serializer_class = StudentActivitySerializer
    permission_classes = [IsAuthenticated]

class BehavioralAssessmentListView(generics.ListCreateAPIView):
    queryset = BehavioralAssessment.objects.all()
    serializer_class = BehavioralAssessmentSerializer
    permission_classes = [IsAuthenticated]

class BehavioralAssessmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = BehavioralAssessment.objects.all()
    serializer_class = BehavioralAssessmentSerializer
    permission_classes = [IsAuthenticated]
