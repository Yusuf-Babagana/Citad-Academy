from rest_framework import serializers
from .models import Exam, Questions, ExamAttempt, ManualScore

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'subject', 'teacher', 'school', 'is_published']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['id', 'school', 'question_text', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'topic']




from rest_framework import serializers
from .models import ExamCategory, Exam

class ExamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = ['id', 'category_type', 'name', 'year']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'subject', 'teacher', 'school', 'name', 'category', 'number_of_questions', 'duration', 'is_global', 'is_published', 'created_at', 'updated_at']


from django.db import transaction
from .models import Questions, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']

class QuestionsSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    question_text = serializers.CharField(style={'base_template': 'textarea.html'})
    explanation = serializers.CharField(style={'base_template': 'textarea.html'}, allow_blank=True, required=False)

    class Meta:
        model = Questions
        fields = ['id', 'exam', 'school', 'topic', 'subtopic', 'instructions', 'question_text', 'explanation', 'question_image', 'question_pdf', 'options', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        options_data = self.context['request'].data.get('options')
        question = Questions.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question
    
class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'student_exam', 'questions', 'current_question_index', 'start_time', 'end_time', 'time_remaining', 'score', 'completed']

    def create(self, validated_data):
        exam_attempt = ExamAttempt.objects.create(**validated_data)
        return exam_attempt

    def update(self, instance, validated_data):
        # Handle updates to the ExamAttempt, custom logic can go here
        return super().update(instance, validated_data)
    
class ManualScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualScore
        fields = ['id', 'student', 'subject', 'teacher', 'ca1_score', 'ca2_score', 'exam_score', 'total_score', 'date_assigned']