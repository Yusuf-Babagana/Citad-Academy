# exam_management/models.py
from django.apps import apps
from django.utils import timezone
from django.db import models
from class_management.models import Subject, Teacher
from school_management.models import School
from subject_management.models import Topic, SubTopic
from random import shuffle
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from ckeditor.fields import RichTextField
from markdownx.models import MarkdownxField 
import mammoth  # To convert .docx to HTML
from io import BytesIO
from tinymce.models import HTMLField

class ExamCategory(models.Model):
    CATEGORY_CHOICES = [
        ('CITAD', 'CENTER FOR INFORMATION TECHNOLOGY AND DEVELOPMENT'),
        ('POLY', 'Polytechnic'),
        ('COE', 'College of Education'),
        ('WAEC', 'WAEC'),
        ('NECO', 'NECO'),
        ('JAMB', 'JAMB'),
    ]
    category_type = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='CITAD')
    name = models.CharField(max_length=255)  # e.g., Name of the university, subject for WAEC/NECO, or year for JAMB
    year = models.IntegerField(null=True, blank=True)  # Year of the exam, applicable for all categories

    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name} ({self.year})"
    
class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='created_exams')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE, related_name='exams')
    number_of_questions = models.IntegerField()
    duration = models.DurationField()  # duration of the exam in minutes
    is_global = models.BooleanField(default=False, help_text="Check if this is a global exam")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject.name} - {self.teacher.user.username}"

class Questions(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    instructions = RichTextField(null=True, blank=True)  
    question_text = HTMLField()
    explanation = HTMLField(null=True, blank=True) 
    question_image = models.ImageField(upload_to='questions/images/', null=True, blank=True)  # Image support
    question_pdf = models.FileField(upload_to='questions/pdfs/', null=True, blank=True)  # PDF support
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text[:50]

    # Method to create a new question with associated options
    @classmethod
    def create_from_parsed_data(cls, exam, school, question_data):
        # Create the question instance
        # Refactored media handling for more complex scenarios
        def append_media(media_list, base_text):
            for media in media_list:
                if media['type'] == 'image':
                    base_text += f"<img src=\"{media['src']}\" alt=\"image\">"
                elif media['type'] == 'mathml':
                    base_text += media['data']
                elif media['type'] == 'latex':
                    base_text += f'<span class="math-tex">{media["data"]}</span>'
                # Additional media types can be handled here
            return base_text

        question_text_with_media = append_media(question_data['media'], question_data['text'])
        question = cls.objects.create(
            exam=exam,
            school=school,
            topic=question_data.get('topic'),
            subtopic=question_data.get('subtopic'),
            question_text=question_text_with_media,
            instructions=question_data.get('instructions', ''),
            explanation=question_data.get('explanation', ''),
        )

        # Handle options
        for option_data in question_data['options']:
            option_text_with_media = append_media(option_data['media'], option_data['text'])
            Option.objects.create(
                question=question,
                option_text=option_text_with_media,
                is_correct=option_data['is_correct'],
            )

        return question

    def __str__(self):
        return self.question_text[:50]

class Option(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='options')
    option_text = HTMLField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text[:50]
    
class ExamAttempt(models.Model):
    student_exam = models.ForeignKey('student_management.StudentExam', on_delete=models.CASCADE, related_name='attempts')
    questions = models.ManyToManyField('exam_management.Questions')
    current_question_index = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_remaining = models.PositiveIntegerField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)  # Field to mark if attempt is completed

    def calculate_score(self):
        total_questions = self.questions.count()
        correct_answers = 0
        
        for question in self.questions.all().prefetch_related('studentexamanswer_set'):
            student_answer_obj = question.studentexamanswer_set.filter(student_exam=self.student_exam).first()
            if student_answer_obj is None:
                continue

            if student_answer_obj.is_correct:
                correct_answers += 1

        # Calculate the percentage score and format it to two decimal places
        percentage_score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
            
        self.score = correct_answers
        self.save()

        return correct_answers, percentage_score

    def complete_attempt(self, request):
        StudentExamAnswer = apps.get_model('student_management', 'StudentExamAnswer')
        Option = apps.get_model('exam_management', 'Option')
            
        # Validation
        if self.current_question_index < self.questions.count() - 1:
            raise ValidationError("Attempt cannot be marked as complete as all questions have not been answered yet.")
            
        # Transaction ensures that these database operations are atomic
        with transaction.atomic():
            # Clear any existing answers for this exam attempt
            StudentExamAnswer.objects.filter(student_exam=self.student_exam).delete()
                
            # Populate StudentExamAnswer with the new answers stored in the session
            for question in self.questions.all():
                answer_id = request.session.get(f'answer_{self.student_exam.exam_id}_{question.id}', None)
                if answer_id:
                    is_correct = Option.objects.get(id=answer_id).is_correct
                    StudentExamAnswer.objects.create(student_exam=self.student_exam, question=question, student_answer_id=answer_id)

            # Mark the attempt as complete and calculate score
            self.end_time = timezone.now()
            self.calculate_score()

            # Clear session data related to this exam attempt
            for key in list(request.session.keys()):
                if key.startswith(f'answer_{self.student_exam.exam_id}_'):
                    del request.session[key]
                    
        self.save()
        
    def get_current_question(self):
        return self.questions.all()[self.current_question_index]

    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index >= self.questions.count():
            self.completed = True  # Mark attempt as completed
            # Optionally, calculate and store score here
        self.save()

# Signal to initialize questions and start time for an ExamAttempt
@receiver(post_save, sender=ExamAttempt)
def initialize_questions(sender, instance, created, **kwargs):
    if created:  # Only if creating a new ExamAttempt
        # Initialize questions
        question_ids = list(instance.student_exam.exam.questions.values_list('id', flat=True))
        shuffle(question_ids)
        instance.questions.set(question_ids)
        
        # Set start time
        instance.start_time = timezone.now()
        instance.save()


class ManualScore(models.Model):
    student = models.ForeignKey('student_management.Student', on_delete=models.CASCADE, related_name='manual_scores')
    subject = models.ForeignKey('class_management.Subject', on_delete=models.CASCADE, related_name='manual_scores')
    teacher = models.ForeignKey('class_management.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='given_scores')
    ca1_score = models.PositiveIntegerField(null=True, blank=True)  # Continuous Assessment 1
    ca2_score = models.PositiveIntegerField(null=True, blank=True)  # Continuous Assessment 2
    exam_score = models.PositiveIntegerField(null=True, blank=True)  # Exam Score
    total_score = models.PositiveIntegerField(null=True, blank=True)  # Auto-calculated Total score
    date_assigned = models.DateField(default=timezone.now)

    def __str__(self):
        student_name = self.student.user.get_full_name() or self.student.user.username
        return f"{student_name} - {self.subject.name} - Total Score: {self.total_score}"

    def save(self, *args, **kwargs):
        # Recalculate total_score every time to ensure it's up-to-date with individual score components
        self.total_score = sum(filter(None, [self.ca1_score, self.ca2_score, self.exam_score]))
        
        # Optional: Add validation for individual scores here if needed (e.g., maximum score limits)
        # if self.ca1_score > MAX_SCORE or self.ca2_score > MAX_SCORE or self.exam_score > MAX_SCORE:
        #     raise ValidationError("Scores exceed the maximum allowed value.")

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('student', 'subject', 'date_assigned')