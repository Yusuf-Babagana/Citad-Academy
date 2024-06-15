# performance_tracking/models.py
from django.db import models
from django.db.models import Avg, Sum
from student_management.models import Student, StudentActivity, BehavioralAssessment
from subject_management.models import Subject
from exam_management.models import ManualScore, ExamAttempt

class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)  # e.g., 'Fall 2023'
    year = models.IntegerField()  # e.g., 2023
    teacher_comments = models.TextField(blank=True)

    def calculate_overall_performance(self):
        """
        Calculates overall performance based on various assessments.
        """
        # Fetching the average score of exams taken by the student for the subject
        exam_scores = self.student.taken_exams.filter(exam__subject=self.subject).aggregate(Avg('score'))['score__avg'] or 0

        # Fetching the sum of total scores from ManualScore for the subject
        manual_scores = self.student.manual_scores.filter(subject=self.subject).aggregate(Sum('total_score'))['total_score__sum'] or 0

        activities_score = self.get_activities_score()
        behavioral_score = self.get_behavioral_score()

        # Example of a weighted average calculation. Adjust weights as needed.
        overall_performance = (exam_scores * 0.4) + (manual_scores * 0.4) + (activities_score * 0.1) + (behavioral_score * 0.1)
        return overall_performance

    def get_activities_score(self):
        """
        Calculates a score based on student activities.
        """
        activity_count = StudentActivity.objects.filter(student=self.student).count()
        # Assuming each activity adds a fixed score, e.g., 5 points per activity
        return activity_count * 5

    def get_behavioral_score(self):
        """
        Calculates a score based on behavioral assessments.
        """
        positive_behaviors = BehavioralAssessment.objects.filter(student=self.student, score__gt=0).aggregate(Sum('score'))['score__sum'] or 0
        negative_behaviors = BehavioralAssessment.objects.filter(student=self.student, score__lt=0).aggregate(Sum('score'))['score__sum'] or 0
        return positive_behaviors + negative_behaviors  # Negative values will reduce the score

    def get_detailed_exam_attempts(self, limit=None):
        exam_attempts = ExamAttempt.objects.filter(student_exam__student=self.student).order_by('-start_time')

        if limit is not None:
            exam_attempts = exam_attempts[:limit]

        detailed_attempts = []
        for attempt in exam_attempts:
            detailed_attempts.append({
                'exam_name': attempt.student_exam.exam.name,
                'score': attempt.score,
                'completed': attempt.completed,
                'start_time': attempt.start_time,
                'end_time': attempt.end_time
            })
        
        return detailed_attempts

    def get_detailed_manual_scores(self):
        """
        Retrieves detailed manual scores for the subject.
        """
        scores = self.student.manual_scores.filter(subject=self.subject)
        detailed_scores = []
        for score in scores:
            detailed_scores.append({
                'ca1_score': score.ca1_score,
                'ca2_score': score.ca2_score,
                'exam_score': score.exam_score,
                'total_score': score.total_score,
                'date_assigned': score.date_assigned,
            })
        return detailed_scores

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.term} {self.year}"
    
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    # ... methods to calculate total days present, absent, and attendance percentage ...

class ExtraCurricularActivity(models.Model):
    student = models.ForeignKey('student_management.Student', on_delete=models.CASCADE, related_name='extra_curricular_activities')
    activity_name = models.CharField(max_length=100)
    achievements = models.TextField(blank=True)

    # ... other fields and methods as needed ...

class ReportCard(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='report_card')
    overall_summary = models.TextField()
    digital_signature_teacher = models.ImageField(upload_to='signatures/', blank=True)
    digital_signature_principal = models.ImageField(upload_to='signatures/', blank=True)

    # ... methods for generating report card data ...