from .models import Leaderboard
from .serializers import LeaderboardSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class LeaderboardListView(generics.ListAPIView):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        school_id = self.request.query_params.get('school_id')
        subject_id = self.request.query_params.get('subject_id')
        classroom_id = self.request.query_params.get('classroom_id')
        exam_id = self.request.query_params.get('exam_id')
        
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)

        return queryset

class LeaderboardDetailView(generics.RetrieveAPIView):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]
