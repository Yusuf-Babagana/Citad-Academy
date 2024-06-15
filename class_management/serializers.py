from rest_framework import serializers
from .models import Class, Teacher, Subject

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'school']

class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'full_name', 'classes', 'is_approved', 'field_of_study']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name and obj.user.last_name else obj.user.username

class SubjectSerializer(serializers.ModelSerializer):
    teachers_names = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'class_related', 'teachers', 'teachers_names']

    def get_teachers_names(self, obj):
        return [f"{teacher.user.first_name} {teacher.user.last_name}" for teacher in obj.teachers.all()]
