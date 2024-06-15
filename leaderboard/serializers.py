from rest_framework import serializers
from .models import Leaderboard

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = ['id', 'student', 'score', 'rank']

from rest_framework import serializers
from .models import Leaderboard

class LeaderboardSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True, allow_null=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    class_name = serializers.CharField(source='classroom.name', read_only=True, allow_null=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True, allow_null=True)

    class Meta:
        model = Leaderboard
        fields = ['id', 'student', 'student_username', 'school', 'school_name', 'subject', 'subject_name', 'classroom', 'class_name', 'exam', 'exam_name', 'score', 'rank', 'is_independent_learner']
