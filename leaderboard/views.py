from django.shortcuts import render, get_object_or_404
from rest_framework import generics, pagination
from .models import Leaderboard
from .serializers import LeaderboardSerializer
from django.db.models import F, Sum, Count
from class_management.models import Class, Subject, School
from student_management.models import Student

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LeaderboardList(generics.ListCreateAPIView):
    serializer_class = LeaderboardSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Leaderboard.objects.all().order_by('-score')
        queryset = queryset.annotate(
            student_name=F('student__user__username'),
            class_name=F('classroom__name'),
        )
        class_id = self.request.query_params.get('class', None)
        if class_id is not None:
            queryset = queryset.filter(classroom_id=class_id)
        return queryset

class LeaderboardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer

def index(request):
    return render(request, 'leaderboard/index.html')

# new view to display leaderboard for a given class
def class_leaderboard(request, class_id):
    # Fetch the Class instance from the database
    class_obj = get_object_or_404(Class, id=class_id)

    # Fetch the Leaderboard entries related to the class
    leaderboard_entries = Leaderboard.objects.filter(classroom=class_obj).order_by('rank')

    return render(request, 'leaderboard/class_leaderboard.html', {
        'class_obj': class_obj,
        'leaderboard_entries': leaderboard_entries,
    })

# new view to display leaderboard for a given subject
def subject_leaderboard(request, subject_id):
    # Fetch the Subject instance from the database
    subject_obj = get_object_or_404(Subject, id=subject_id)

    # Fetch the Leaderboard entries related to the subject
    leaderboard_entries = Leaderboard.objects.filter(subject=subject_obj).order_by('rank')

    return render(request, 'leaderboard/subject_leaderboard.html', {
        'subject_obj': subject_obj,
        'leaderboard_entries': leaderboard_entries,
    })

# New view to display leaderboard for independent learners
def independent_leaderboard(request, subject_id):
    subject_obj = get_object_or_404(Subject, id=subject_id)
    leaderboard_entries = Leaderboard.objects.filter(subject=subject_obj, classroom=None).order_by('rank')

    return render(request, 'leaderboard/independent_leaderboard.html', {
        'subject_obj': subject_obj,
        'leaderboard_entries': leaderboard_entries,
    })

# New view to display leaderboard for schools based on student performance
def school_leaderboard(request):
    schools = School.objects.annotate(
        total_score=Sum('students__leaderboards__score', filter=F('students__leaderboards__score__isnull=False')),
        total_students=Count('students')
    ).order_by('-total_score')

    return render(request, 'leaderboard/school_leaderboard.html', {
        'schools': schools,
    })