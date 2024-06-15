from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View
from rest_framework import generics, exceptions
from django.views import generic
from .models import Student, EnrollmentRequest, StudentExam, StudentExamAnswer, StudentPerformance, StudentActivity, BehavioralAssessment
from .serializers import StudentSerializer, EnrollmentRequestSerializer
from .forms import SubjectSelectionForm, StudentPerformanceForm, StudentActivityForm, BehavioralAssessmentForm
from exam_management.models import Exam
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.generic.edit import FormView




class StudentList(generics.ListCreateAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'school_admin'):
            return Student.objects.filter(user__school=self.request.user.school_admin.school)
        elif hasattr(self.request.user, 'teacher'):
            return Student.objects.filter(enrolled_class__in=self.request.user.teacher.classes.all())
        elif hasattr(self.request.user, 'student'):
            return Student.objects.filter(id=self.request.user.student.id)
        else:
            return Student.objects.none()

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'school_admin'):
            return Student.objects.filter(user__school=self.request.user.school_admin.school)
        elif hasattr(self.request.user, 'teacher'):
            return Student.objects.filter(enrolled_class__in=self.request.user.teacher.classes.all())
        elif hasattr(self.request.user, 'student'):
            return Student.objects.filter(id=self.request.user.student.id)
        else:
            return Student.objects.none()

class EnrollmentRequestList(View):
    def get(self, request):
        if hasattr(request.user, 'school_admin'):
            pending_requests = EnrollmentRequest.objects.filter(
                school=request.user.school_admin.school, is_approved__isnull=True)
        else:
            pending_requests = EnrollmentRequest.objects.none()

        return render(request, 'student_management/enrollment_request_list.html', {
            'pending_requests': pending_requests
        })

    def post(self, request):
        selected_requests = request.POST.getlist('selected_requests')
        action = request.POST.get('action')

        if action == 'approve':
            EnrollmentRequest.objects.filter(id__in=selected_requests).update(is_approved=True)
        elif action == 'reject':
            EnrollmentRequest.objects.filter(id__in=selected_requests).update(is_approved=False)

        # Redirecting to the same page to reflect the changes
        return redirect('student:enrollment-request-list')

class EnrollmentRequestDetail(View):
    def get(self, request, pk):
        if hasattr(request.user, 'school_admin'):
            try:
                enrollment_request = EnrollmentRequest.objects.get(
                    pk=pk, school=request.user.school_admin.school)
            except EnrollmentRequest.DoesNotExist:
                # Handle error here, maybe redirect to an error page
                return redirect('error_page')
        else:
            # Handle error here, maybe redirect to an error page
            return redirect('error_page')

        return render(request, 'student_management/enrollment_request_detail.html', {
            'enrollment_request': enrollment_request
        })

    def post(self, request, pk):
        action = request.POST.get('action')
        if hasattr(request.user, 'school_admin'):
            try:
                enrollment_request = EnrollmentRequest.objects.get(
                    pk=pk, school=request.user.school_admin.school)

                if action == 'approve':
                    enrollment_request.is_approved = True

                    # If it's a teacher's request, update the teacher's status
                    if enrollment_request.teacher:
                        enrollment_request.teacher.is_approved = True
                        enrollment_request.teacher.save()

                    # If it's a student's request, update the student's status
                    if enrollment_request.student:
                        enrollment_request.student.is_approved = True
                        enrollment_request.student.save()

                elif action == 'reject':
                    enrollment_request.is_approved = False

                enrollment_request.save()
            except EnrollmentRequest.DoesNotExist:
                # Handle error here, maybe redirect to an error page
                return redirect('error_page')
        else:
            # Handle error here, maybe redirect to an error page
            return redirect('error_page')

        # Redirecting to the same page or another page as needed
        return redirect('user_management:school-admin-dashboard')

# new view to serve the template
def index(request):
    return render(request, 'student_management/index.html')
 
    
class SubjectSelectionView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Fetch the logged in User instance
        user = request.user

        # Get the student instance related to the user
        student = Student.objects.get(user=user)

        # Initialize the form with the current subject combination of the student
        form = SubjectSelectionForm(instance=student.subject_combination)

        return render(request, 'student_management/subject_selection.html', {
            'form': form,
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # Fetch the logged in User instance
        user = request.user

        # Get the student instance related to the user
        student = Student.objects.get(user=user)

        # Update the student's subject combination with the submitted form data
        form = SubjectSelectionForm(request.POST, instance=student.subject_combination)
        if form.is_valid():
            form.save()

        return redirect('user_management:student_dashboard')


class StudentPerformanceCreateView(generic.CreateView):
    model = StudentPerformance
    form_class = StudentPerformanceForm
    template_name = 'student_management/student_performance_form.html'
    success_url = reverse_lazy('student_performance_list')  # Adjust the URL name as needed

class StudentPerformanceUpdateView(generic.UpdateView):
    model = StudentPerformance
    form_class = StudentPerformanceForm
    template_name = 'student_management/student_performance_form.html'
    success_url = reverse_lazy('student_performance_list')  # Adjust the URL name as needed

class StudentActivityCreateView(generic.CreateView):
    model = StudentActivity
    form_class = StudentActivityForm
    template_name = 'student_management/student_activity_form.html'
    success_url = reverse_lazy('student_activity_list')  # Adjust the URL name as needed

class StudentActivityUpdateView(generic.UpdateView):
    model = StudentActivity
    form_class = StudentActivityForm
    template_name = 'student_management/student_activity_form.html'
    success_url = reverse_lazy('student_activity_list')  # Adjust the URL name as needed

class BehavioralAssessmentCreateView(generic.CreateView):
    model = BehavioralAssessment
    form_class = BehavioralAssessmentForm
    template_name = 'student_management/behavioral_assessment_form.html'
    success_url = reverse_lazy('behavioral_assessment_list')  # Adjust the URL name as needed

class BehavioralAssessmentUpdateView(generic.UpdateView):
    model = BehavioralAssessment
    form_class = BehavioralAssessmentForm
    template_name = 'student_management/behavioral_assessment_form.html'
    success_url = reverse_lazy('behavioral_assessment_list')  # Adjust the URL name as needed

