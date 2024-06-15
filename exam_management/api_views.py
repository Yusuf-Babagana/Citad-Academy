from rest_framework import generics
from .models import ExamCategory, Exam, Questions, Option
from .serializers import ExamCategorySerializer, ExamSerializer, QuestionsSerializer, OptionSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

class ExamCategoryListView(generics.ListCreateAPIView):
    queryset = ExamCategory.objects.all()
    serializer_class = ExamCategorySerializer

class ExamCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamCategory.objects.all()
    serializer_class = ExamCategorySerializer

class ExamListView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def set_correct(self, request, pk=None):
        option = self.get_object()
        option.is_correct = True
        option.save()
        return Response({'status': 'option set as correct'})
    
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExamAttempt
from .serializers import ExamAttemptSerializer

class ExamAttemptViewSet(viewsets.ModelViewSet):
    queryset = ExamAttempt.objects.all()
    serializer_class = ExamAttemptSerializer

    @action(detail=True, methods=['post'])
    def complete_attempt(self, request, pk=None):
        exam_attempt = self.get_object()
        try:
            exam_attempt.complete_attempt(request)
            return Response({"status": "Attempt marked as complete", "score": exam_attempt.score}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"status": "Error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
from .models import ManualScore
from .serializers import ManualScoreSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class ManualScoreListView(generics.ListCreateAPIView):
    queryset = ManualScore.objects.all()
    serializer_class = ManualScoreSerializer
    permission_classes = [IsAuthenticated]

class ManualScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ManualScore.objects.all()
    serializer_class = ManualScoreSerializer
    permission_classes = [IsAuthenticated]
