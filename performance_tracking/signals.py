#performance_tracking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from exam_management.models import ExamAttempt, ManualScore
from student_management.models import StudentActivity, BehavioralAssessment
from performance_tracking.models import Performance

@receiver(post_save, sender=ExamAttempt)
def update_performance_on_exam_completion(sender, instance, **kwargs):
    if instance.completed:
        student = instance.student_exam.student
        subject = instance.student_exam.exam.subject
        term = 'Current Term'  # Adjust as needed
        year = 2023  # Adjust as needed

        performance, created = Performance.objects.update_or_create(
            student=student,
            subject=subject,
            term=term,
            year=year,
            defaults={'term': term, 'year': year}
        )

        # Recalculate overall performance after updating/creating
        performance.calculate_overall_performance()
        performance.save()

@receiver(post_save, sender=ManualScore)
def update_performance_on_manual_score(sender, instance, **kwargs):
    performance, created = Performance.objects.update_or_create(
        student=instance.student,
        subject=instance.subject,
        term='Current Term',  # Adjust as needed
        year=2023,  # Adjust as needed
        defaults={'term': 'Current Term', 'year': 2023}
    )

    # Recalculate overall performance after updating/creating
    performance.calculate_overall_performance()
    performance.save()

@receiver(post_save, sender=StudentActivity)
def update_performance_on_activity(sender, instance, **kwargs):
    # Adjust logic as needed
    Performance.objects.update_or_create(
        student=instance.student,
        subject=instance.subject,  # Assuming a subject field is available
        term='Current Term',
        year=2023,
        defaults={'term': 'Current Term', 'year': 2023})

@receiver(post_save, sender=BehavioralAssessment)
def update_performance_on_behavioral_assessment(sender, instance, **kwargs):
    Performance.objects.update_or_create(
        student=instance.student,
        subject=instance.subject,  # Assuming a subject field is available
        term=instance.term,
        year=instance.year,
        defaults={'term': instance.term, 'year': instance.year})
