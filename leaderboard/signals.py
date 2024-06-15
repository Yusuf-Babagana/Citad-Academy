from django.db.models.signals import post_save
from django.dispatch import receiver
from student_management.models import StudentExam
from leaderboard.models import Leaderboard

@receiver(post_save, sender=StudentExam)
def update_leaderboard(sender, instance, **kwargs):
    student_exam = instance

    if student_exam.student is None:
        return  # Do nothing if there is no associated student

    subject = student_exam.exam.subject

    # Classroom might be None for Independent Learners
    classroom = student_exam.student.enrolled_class if hasattr(student_exam.student, 'enrolled_class') else None

    leaderboard_entry, created = Leaderboard.objects.get_or_create(
        student=student_exam.student,
        subject=subject,
        classroom=classroom,  # This might be None
        defaults={'score': student_exam.score}
    )

    if not created and student_exam.score > leaderboard_entry.score:
        leaderboard_entry.score = student_exam.score
        leaderboard_entry.save()

    # After updating the score, update the ranks for all Leaderboard entries for this subject and class
    update_ranks(subject, classroom)


def update_ranks(subject, classroom=None):
    # Get all Leaderboard entries for this subject and optional classroom, ordered by score
    # Independent learners will have classroom=None
    leaderboard_entries = Leaderboard.objects.filter(
        subject=subject,
        classroom=classroom
    ).order_by('-score')

    # Loop through the entries and update their rank
    for i, entry in enumerate(leaderboard_entries):
        entry.rank = i + 1  # rank should start at 1, not 0
        entry.save()
