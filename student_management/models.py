# student_management/models.py
from django.db import models
from user_management.models import User
from class_management.models import Subject, Teacher
from exam_management.models import Exam, Questions, Option
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey('class_management.Class', on_delete=models.SET_NULL, null=True)
    subjects = models.ManyToManyField('class_management.Subject', related_name='students')
    class_name = models.CharField(max_length=100)
    is_independent_learner = models.BooleanField(default=False)

    # New fields to be added
    grade = models.CharField(max_length=50, default='N/A')  # e.g., "Grade 10"
    student_id = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Unique Student ID
    parent_contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}' if self.user.first_name and self.user.last_name else self.user.username
        return f'{full_name} - Class_name: {self.class_name}'

class StudentExam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_exams', null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_takers')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)
    time_remaining = models.IntegerField(null=True, blank=True)

    @property
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() // 60  # returns duration in minutes
        return None

    @property
    def time_remaining(self):
        if self.start_time and not self.end_time:
            elapsed_time = timezone.now() - self.start_time
            elapsed_time_in_minutes = elapsed_time.total_seconds() // 60
            return self.exam.duration - elapsed_time_in_minutes
        return None

    def get_status(self):
        if self.start_time and self.end_time:
            return 'Completed'
        elif self.start_time:
            return 'Ongoing'
        else:
            return 'Not Started'

class StudentExamAnswer(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    student_answer = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('student_exam', 'question')

    @property
    def is_correct(self):
        return self.student_answer.is_correct if self.student_answer else False

    def get_selected_option_display(self):
        return self.student_answer.option_text if self.student_answer else "No answer selected"

class EnrollmentRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    school = models.ForeignKey('school_management.School', on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey('class_management.Class', on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(null=True, default=None)

    def __str__(self):
        requester = self.student.user.get_full_name() if self.student else self.teacher.user.get_full_name()
        field_or_class = self.student.class_or_department if self.student else self.teacher.field_of_study
        status = "Approved" if self.is_approved else "Rejected" if self.is_approved is False else "Pending"
        return f'{requester} - {field_or_class} - {self.school.name} - {status}'
        
    
class SubjectCombination(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='subject_combination')
    subjects = models.ManyToManyField(Subject)
    
    def __str__(self):
        return f"{self.student.user.username}'s subjects"
    

class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    year = models.IntegerField()
    grade = models.CharField(max_length=5)
    # Add additional fields as necessary

    def __str__(self):
        return f'Performance: {self.student} - {self.subject} - {self.term} {self.year}'

class StudentActivity(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')
    activity_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    participation_level = models.CharField(max_length=50)
    # Add additional fields as necessary

    def __str__(self):
        return f'Activity: {self.activity_name} - {self.student}'

class BehavioralAssessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='behavioral_assessments')
    term = models.CharField(max_length=20)
    year = models.IntegerField()
    behavior = models.CharField(max_length=255)
    score = models.IntegerField()
    # Add additional fields as necessary

    def __str__(self):
        return f'Behavioral Assessment: {self.student} - {self.term} {self.year}'