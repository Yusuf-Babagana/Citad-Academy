# performance_tracking/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Performance, AttendanceRecord, ExtraCurricularActivity, ReportCard, BehavioralAssessment
from student_management.models import Student
from django.utils import timezone
from django.db.models import Avg

def calculate_overall_performance(request, student_id, subject_id, term, year):
    """
    View to calculate and display the overall performance of a student for a specific subject and term.
    """
    student = get_object_or_404(Student, pk=student_id)
    performance, created = Performance.objects.get_or_create(
        student=student, 
        subject_id=subject_id, 
        term=term, 
        year=year
    )

    overall_performance = performance.calculate_overall_performance()
    context = {
        'student': student,
        'performance': overall_performance,
        'term': term,
        'year': year
    }
    return render(request, 'performance/overall_performance.html', context)

def view_academic_performance(request, student_id, subject_id):
    """
    View to display academic performance details of a student for a specific subject.
    """
    student = get_object_or_404(Student, pk=student_id)
    performance = Performance.objects.filter(
        student=student, 
        subject_id=subject_id, 
        term='Current Term',  # Adjust as needed
        year=timezone.now().year  # Adjust as needed
    ).first()

    if performance:
        detailed_scores = performance.get_detailed_manual_scores()
        detailed_exam_attempts = performance.get_detailed_exam_attempts()
    else:
        detailed_scores = []
        detailed_exam_attempts = []

    context = {
        'student': student,
        'performance': performance,
        'detailed_scores': detailed_scores,
        'detailed_exam_attempts': detailed_exam_attempts,
    }
    return render(request, 'performance/academic_performance.html', context)

def view_activities_score(request, student_id):
    """
    View to display activities score of a student.
    """
    student = get_object_or_404(Student, pk=student_id)
    performance = Performance(student=student)
    activities_score = performance.get_activities_score()
    context = {
        'student': student,
        'activities_score': activities_score
    }
    return render(request, 'performance/activities_score.html', context)

def view_behavioral_score(request, student_id):
    """
    View to display behavioral score of a student.
    """
    student = get_object_or_404(Student, pk=student_id)
    performance = Performance(student=student)
    behavioral_score = performance.get_behavioral_score()
    context = {
        'student': student,
        'behavioral_score': behavioral_score
    }
    return render(request, 'performance/behavioral_score.html', context)

def calculate_student_position(student, performances):
    # Get all students in the same class
    class_students = Student.objects.filter(enrolled_class=student.enrolled_class)
    
    # Calculate the average score for each student in the class
    student_scores = {}
    for s in class_students:
        total_score = sum(perf.calculate_overall_performance() for perf in s.performances.filter(year=timezone.now().year))
        average_score = total_score / s.performances.filter(year=timezone.now().year).count() if s.performances.filter(year=timezone.now().year).count() > 0 else 0
        student_scores[s.id] = average_score

    # Sort the students by their average score in descending order
    sorted_scores = sorted(student_scores.items(), key=lambda x: x[1], reverse=True)

    # Find the rank of the current student
    student_rank = next((index for (index, (s_id, score)) in enumerate(sorted_scores, start=1) if s_id == student.id), None)
    
    return student_rank

def individual_student_report(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # Fetching academic performances
    performances = Performance.objects.filter(student__id=student_id)

    # Fetching attendance records
    attendance_records = AttendanceRecord.objects.filter(student=student)

    # Fetching extra-curricular activities
    activities = ExtraCurricularActivity.objects.filter(student=student)

    # Fetching behavioral scores - Assuming there's a method or model for this
    behavioral_scores = BehavioralAssessment.objects.filter(student=student)

    # Fetching the overall report card summary
    report_card = ReportCard.objects.filter(student=student).first()

    school_logo = None
    if student.enrolled_class and student.enrolled_class.school and student.enrolled_class.school.logo:
        school_logo = student.enrolled_class.school.logo.url

    # Calculate average score and position as before
    average_score = sum(perf.calculate_overall_performance() for perf in performances) / performances.count() if performances.count() > 0 else 0
    position = calculate_student_position(student, performances)

    context = {
        'student': student,
        'performances': performances,
        'attendance_records': attendance_records,
        'activities': activities,
        'behavioral_scores': behavioral_scores,
        'report_card': report_card,
        'average_score': average_score,
        'position': position,
        'school_logo': school_logo,
        'profile_image': student.user.profile_image.url if student.user.profile_image else None,
    }
   
    return render(request, 'performance_tracking/individual_report.html', context)


def generate_report_card_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # Fetching academic performances and detailed scores
    performances = Performance.objects.filter(student=student)

    detailed_manual_scores = {}
    detailed_exam_attempts = {}

    # Specify the limit for the number of exam attempts you want to display
    attempts_limit = 5

    for performance in performances:
        # Fetching detailed manual scores
        detailed_manual_scores[performance.subject.name] = performance.get_detailed_manual_scores()

        # Fetching detailed exam attempts with a limit
        attempts = performance.get_detailed_exam_attempts(limit=attempts_limit)
        if attempts:
            detailed_exam_attempts[performance.subject.name] = attempts

    attendance_records = AttendanceRecord.objects.filter(student=student)
    activities = ExtraCurricularActivity.objects.filter(student=student)
    behavioral_scores = BehavioralAssessment.objects.filter(student=student)
    report_card = ReportCard.objects.filter(student=student).first()

    context = {
        'student': student,
        'performances': performances,
        'detailed_exam_attempts': detailed_exam_attempts,
        'detailed_manual_scores': detailed_manual_scores,
        'attendance_records': attendance_records,
        'activities': activities,
        'behavioral_scores': behavioral_scores,
        'report_card': report_card,
        # ... other context data ...
    }

    return render(request, 'performance_tracking/full_report_card.html', context)