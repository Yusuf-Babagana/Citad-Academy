from django.db import models
from student_management.models import Student
from class_management.models import Class, Subject
from school_management.models import School  # Assuming this import
from exam_management.models import Exam  # Assuming this import

class Leaderboard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leaderboards')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='leaderboards', null=True, blank=True)  # new field
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='leaderboards', null=True, blank=True)
    classroom = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='leaderboards', null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='leaderboards', null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    rank = models.PositiveIntegerField(null=True)
    is_independent_learner = models.BooleanField(default=False)

    class Meta:
        unique_together = [['student', 'subject', 'classroom', 'exam', 'school']]  # updated unique constraint

    def __str__(self):
        return f"{self.rank}. {self.student.user.username} - {self.score}"
