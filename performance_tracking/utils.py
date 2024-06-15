#performance_tracking/utils.py
from django.db.models import Avg, Max, Min, Sum, Count
from exam_management.models import ExamAttempt, ManualScore
from student_management.models import StudentPerformance, StudentActivity, BehavioralAssessment

def get_detailed_exam_attempts_for_class(class_id):
    """
    Returns detailed exam attempt information for each student in a class.
    """
    detailed_attempts = (
        ExamAttempt.objects.filter(student_exam__student__enrolled_class_id=class_id)
        .values('student_exam__student', 'student_exam__exam__name', 'score', 'completed', 'start_time', 'end_time')
    )

    attempts_by_student = {}
    for attempt in detailed_attempts:
        student_id = attempt['student_exam__student']
        if student_id not in attempts_by_student:
            attempts_by_student[student_id] = []
        attempts_by_student[student_id].append({
            'exam_name': attempt['student_exam__exam__name'],
            'score': attempt['score'],
            'completed': attempt['completed'],
            'start_time': attempt['start_time'],
            'end_time': attempt['end_time'],
        })

    return attempts_by_student

def get_detailed_manual_scores_for_class(class_id):
    """
    Returns detailed manual score information for each student in a class.
    """
    detailed_scores = ManualScore.objects.filter(student__enrolled_class_id=class_id)
    scores_by_student = {}

    for score in detailed_scores:
        student_id = score.student.id
        if student_id not in scores_by_student:
            scores_by_student[student_id] = []
        scores_by_student[student_id].append({
            'subject': score.subject.name,
            'ca1_score': score.ca1_score,
            'ca2_score': score.ca2_score,
            'exam_score': score.exam_score,
            'total_score': score.total_score,
            'date_assigned': score.date_assigned,
            'teacher': score.teacher.get_full_name() if score.teacher else 'N/A',
        })

    return scores_by_student

def get_class_topper(exam_scores, manual_scores):
    # Assuming exam_scores and manual_scores are dictionaries with student ids as keys
    # and their score stats as values, as returned by the previous step's functions.
    class_scores = {}
    for student_id in exam_scores:
        class_scores[student_id] = {
            'exam_total': exam_scores[student_id]['total'],
            'manual_total': manual_scores.get(student_id, {}).get('total', 0),
        }

    # Calculate the overall total for each student and identify the topper
    overall_scores = {student_id: scores['exam_total'] + scores['manual_total'] for student_id, scores in class_scores.items()}
    class_topper = max(overall_scores, key=overall_scores.get)  # This gives you the student_id of the class topper

    return class_topper, overall_scores[class_topper]

def get_student_performance_trends(student_id):
    return StudentPerformance.objects.filter(student__id=student_id).order_by('-year', '-term')

def get_student_activities(student_id):
    return StudentActivity.objects.filter(student__id=student_id)

def get_student_behavioral_assessments(student_id):
    return BehavioralAssessment.objects.filter(student__id=student_id)
