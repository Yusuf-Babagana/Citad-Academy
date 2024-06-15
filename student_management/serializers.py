from rest_framework import serializers
from .models import Student, EnrollmentRequest

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'enrolled_class']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = '__all__'

from rest_framework import serializers
from .models import (
    Student, StudentExam, StudentExamAnswer, EnrollmentRequest, SubjectCombination,
    StudentPerformance, StudentActivity, BehavioralAssessment
)
from class_management.models import Subject

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'enrolled_class', 'subjects', 'class_name', 'is_independent_learner', 'grade', 'student_id', 'parent_contact']

class StudentExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExam
        fields = ['id', 'student', 'exam', 'start_time', 'end_time', 'score', 'time_remaining']

class StudentExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamAnswer
        fields = ['id', 'student_exam', 'question', 'student_answer', 'is_correct']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'teacher', 'school', 'enrolled_class', 'is_approved']

class SubjectCombinationSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(many=True, queryset=Subject.objects.all())

    class Meta:
        model = SubjectCombination
        fields = ['id', 'student', 'subjects']

class StudentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPerformance
        fields = ['id', 'student', 'subject', 'term', 'year', 'grade']

class StudentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentActivity
        fields = ['id', 'student', 'activity_name', 'description', 'participation_level']

class BehavioralAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralAssessment
        fields = ['id', 'student', 'term', 'year', 'behavior', 'score']
