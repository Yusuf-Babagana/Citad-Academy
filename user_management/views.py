# user_management/views.py
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.views import View
from rest_framework import generics
from .models import User
from school_management.models import SchoolAdmin, School  # import the School model
from student_management.models import Student
from class_management.models import Teacher
#from .serializers import UserSerializer 
from .forms import SchoolAdminRegisterForm, TeacherRegisterForm, StudentRegisterForm, AdminRegisterForm, IndependentLearnerRegisterForm, CustomAuthenticationForm, ProfileImageUpdateForm 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from school_management.forms import SchoolForm
from class_management.forms import ClassForm, AssignStudentToClassAndSubjectsForm
from student_management.models import EnrollmentRequest, SubjectCombination, StudentExam, StudentExamAnswer
from student_management.forms import  SubjectSelectionForm, StudentPerformanceForm, StudentActivityForm, BehavioralAssessmentForm
from class_management.forms import SubjectForm, SubjectForm, AssignTeacherToClassForm
from subject_management.forms import TopicForm, SubTopicForm
from class_management.models import Teacher, Subject
from exam_management.forms import ExamForm, QuestionsForm
from exam_management.models import Exam, Questions, ExamAttempt, ExamCategory
from exam_management.views import generate_exam_analysis
from media_management.forms import MediaForm 
from media_management.models import Media
from leaderboard.models import Leaderboard
from django.db.models import Q
from django.http import JsonResponse
from class_management.models import Class
from django.db import transaction
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from performance_tracking.models import Performance

# user_management/views.py API
#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import status, permissions
#from .serializers import RegisterSerializer, UserSerializer
#from django.contrib.auth import authenticate
#from rest_framework_simplejwt.tokens import RefreshToken

#class RegisterAPIView(APIView):
#    def post(self, request, *args, **kwargs):
#        serializer = RegisterSerializer(data=request.data)
#        if serializer.is_valid():
#            user = serializer.save()
#            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#class LoginAPIView(APIView):
#    def post(self, request):
#        username = request.data.get("username")
#        password = request.data.get("password")
#
#        user = authenticate(username=username, password=password)

#        if user is not None:
            # create a token
#            refresh = RefreshToken.for_user(user)

            # add school ID to the user details
#            user_details = UserSerializer(user).data
#            if user.school:
#                user_details["school_id"] = user.school.id

            # Return the token and user details in the response
#            return Response({
#                "refresh": str(refresh),
#                "access": str(refresh.access_token),
#                "user": user_details,   # include user details in the response
#            })
#        else:
#            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
#class CurrentUserView(APIView):
#    """
#    View to retrieve the details of the currently logged in user.
#    """
#    permission_classes = [permissions.IsAuthenticated]

#    def get(self, request):
#        serializer = UserSerializer(request.user)
#        return Response(serializer.data)

# Your existing API views:
#class UserList(generics.ListCreateAPIView):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

#class UserDetail(generics.RetrieveUpdateDestroyAPIView):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

# New view for your index template:
class UserManagementIndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_management/index.html')

class UserManagementIndexView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        return render(request, 'user_management/index.html', {'users': users})
    

class SchoolAdminRegisterView(View):
    def get(self, request, *args, **kwargs):
        form = SchoolAdminRegisterForm()
        return render(request, 'user_management/register_school_admin.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SchoolAdminRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()  # Convert username to lowercase
            user.set_password(form.cleaned_data['password'])
            user.role = 'SA'
            # Set the trial period for the user
            user.trial_start_date = timezone.now()
            user.trial_end_date = timezone.now() + timedelta(days=7)
            user.save()

            # create a School object
            school = School.objects.create(name=form.cleaned_data['school_name'], address=form.cleaned_data['school_address'])

            # create a SchoolAdmin object
            SchoolAdmin.objects.create(user=user, school=school)

            messages.success(request, 'Registration successful. You can now log in.') # Add this line
            return redirect('/user_management/login/')  # Redirect to login page instead of home page
        return render(request, 'user_management/register_school_admin.html', {'form': form})


class TeacherRegisterView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':  # Check if user is authenticated and role is 'SA'
            school = request.user.school_admin.school  # Get the school associated with the logged-in school admin
            form = TeacherRegisterForm(school=school)  # Pass the school as an argument
            return render(request, 'user_management/register_teacher.html', {'form': form})
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':
            form = TeacherRegisterForm(request.POST, request.FILES, school=request.user.school_admin.school)  # Pass the school as an argument
            if form.is_valid():
                with transaction.atomic():  # Ensure atomicity
                    user = form.save(commit=False)
                    user.username = user.username.lower()
                    user.set_password(form.cleaned_data['password'])
                    user.role = 'T'  # Assuming 'T' is for Teachers

                    # Set the school field to the school of the logged-in school admin
                    user.school = request.user.school_admin.school

                    user.save()

                    # Create the Teacher object and associate it with the newly created User
                    field_of_study = form.cleaned_data['field_of_study']
                    teacher = Teacher.objects.create(user=user, field_of_study=field_of_study)
                    
                    # Create EnrollmentRequest object
                    selected_school = form.cleaned_data['school']
                    EnrollmentRequest.objects.create(teacher=teacher, school=selected_school)

                messages.success(request, 'Registration successful. The teacher can now log in.')
                return redirect('/user_management/login/')  # Redirect to login page instead of home page
            return render(request, 'user_management/register_teacher.html', {'form': form})
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")


class StudentRegisterView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':  # Check if user is authenticated and role is 'SA'
            form = StudentRegisterForm(initial={'school': request.user.school_admin.school})
            return render(request, 'user_management/register_student.html', {'form': form})
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':
            form = StudentRegisterForm(request.POST, request.FILES)
            
            if 'school' in request.POST:
                try:
                    selected_school = School.objects.get(id=request.POST['school'])
                    form.fields['class_name'].choices = [(c.id, c.name) for c in Class.objects.filter(school=selected_school)]
                except School.DoesNotExist:
                    messages.error(request, 'The selected school does not exist.')
            
            if form.is_valid():
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = user.username.lower()
                    user.set_password(form.cleaned_data['password'])
                    user.role = 'S'
                    # Set the trial period for the user
                    user.trial_start_date = timezone.now()
                    user.trial_end_date = timezone.now() + timedelta(days=7)
                    user.save()

                    selected_class = Class.objects.get(id=form.cleaned_data['class_name'])
                    student = Student.objects.create(
                        user=user, 
                        class_name=selected_class.name, 
                        enrolled_class=selected_class
                    )
                    
                    SubjectCombination.objects.create(student=student)
                    
                    # Create EnrollmentRequest object
                    EnrollmentRequest.objects.create(student=student, school=user.school)
                    
                    messages.success(request, 'Registration successful. The student can now log in.')
                    return redirect('/user_management/login/')
            
            return render(request, 'user_management/register_student.html', {'form': form})
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")

# Your get_classes view remains the same
def get_classes(request):
    school_id = request.GET.get('school_id', None)
    if school_id:
        classes = Class.objects.filter(school_id=school_id).values('id', 'name')
        class_list = list(classes)
        return JsonResponse({'classes': class_list})
    else:
        return JsonResponse({'classes': []})

class IndependentLearnerRegisterView(View):
    def get(self, request, *args, **kwargs):
        form = IndependentLearnerRegisterForm()
        return render(request, 'user_management/register_independent_learner.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = IndependentLearnerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()  # Convert username to lowercase
            user.set_password(form.cleaned_data['password'])
            user.role = 'IL'  # Setting the role as Independent Learner
            # Set the trial period for the user
            user.trial_start_date = timezone.now()
            user.trial_end_date = timezone.now() + timedelta(days=7)
            user.save()

            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('/user_management/login/')  # make sure the login URL name is correct
        return render(request, 'user_management/register_independent_learner.html', {'form': form})

class AdminRegisterView(View):
    def get(self, request, *args, **kwargs):
        form = AdminRegisterForm()
        return render(request, 'user_management/register_admin.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('/user_management/login/') # make sure the login URL name is correct
        return render(request, 'user_management/register_admin.html', {'form': form})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = CustomAuthenticationForm()
        return render(request, 'user_management/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Store the user's school id in the session
            if user.school:
                request.session['school_id'] = user.school.id
            else:
                request.session['school_id'] = None

            # Redirect to the respective dashboard
            if user.role == 'SA':
                return redirect('/user_management/school_admin_dashboard/')
            elif user.role == 'T':
                return redirect('/user_management/teacher_dashboard/')
            elif user.role == 'S':
                return redirect('/user_management/student_dashboard/')
            elif user.role == 'A':
                return redirect('/user_management/admin_dashboard/')
            elif user.role == 'IL':  # Redirecting independent learner
                return redirect('/user_management/independent_learner_dashboard/')

        return render(request, 'user_management/login.html', {'form': form, 'error': 'Invalid username or password'})
    
def is_school_admin(user):
    return hasattr(user, 'school_admin')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('user_management:login')  # redirect to login page after logout
    
class GetStartedView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_management/get_started.html')

class TakeTourView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_management/take_tour.html')

class SchoolAdminDashboardView(View):
    @method_decorator(login_required(login_url='/user_management/login/'))
    def get(self, request, *args, **kwargs):
        school = request.user.school_admin.school
        school_form = SchoolForm(instance=school)
        class_form = ClassForm()
        subject_form = SubjectForm(school=school)
        assign_teacher_form = AssignTeacherToClassForm(school=school)
        assign_student_form = AssignStudentToClassAndSubjectsForm(school=school)  # Pass the school instance to the form

        # Fetch teachers and students related to the school
        teachers = Teacher.objects.filter(user__school=school, is_approved=True)
        students = Student.objects.filter(user__school=school)

        # Fetch unique classroom IDs that have a leaderboard entry
        class_ids = Leaderboard.objects.filter(classroom__in=school.classes.all()).values_list('classroom', flat=True).distinct()

        # Fetch the corresponding Leaderboard objects
        class_leaderboards = Leaderboard.objects.filter(classroom__in=class_ids)

        # Fetch unique subject IDs that have a leaderboard entry
        subject_ids = Leaderboard.objects.filter(subject__in=Subject.objects.filter(class_related__in=school.classes.all())).values_list('subject', flat=True).distinct()

        # Fetch the corresponding Leaderboard objects
        subject_leaderboards = Leaderboard.objects.filter(subject__in=subject_ids)

        # Fetch pending enrollment requests for the school admin
        pending_requests = EnrollmentRequest.objects.filter(
            school=request.user.school_admin.school, 
            is_approved=None
        ).select_related(
            'student__user',
            'teacher__user',
        )
        
        register_teacher_link = '/user_management/register/teacher/'
        register_student_link = '/user_management/register/student/'
        profile_image = request.user.profile_image.url if request.user.profile_image else None
        profile_image_form = ProfileImageUpdateForm(instance=request.user)

        
        return render(
            request, 
            'user_management/school_admin_dashboard.html', 
            {
                'school_form': school_form, 
                'class_form': class_form, 
                'subject_form': subject_form,
                'assign_teacher_form': assign_teacher_form,
                'assign_student_form': assign_student_form,  
                'class_leaderboards': class_leaderboards,
                'subject_leaderboards': subject_leaderboards,
                'teachers': teachers,  
                'students': students,
                'pending_requests': pending_requests,
                'profile_image': profile_image, 
                'profile_image_form': profile_image_form,
                'register_teacher_link': register_teacher_link,
                'register_student_link': register_student_link
            }
        )

    @method_decorator(login_required(login_url='/user_management/login/'))
    def post(self, request, *args, **kwargs):
        school = request.user.school_admin.school  # Add this line
        school_form = SchoolForm(request.POST, instance=school)
        class_form = ClassForm(request.POST)
        subject_form = SubjectForm(request.POST, school=school)
        assign_teacher_form = AssignTeacherToClassForm(request.POST, school=school)
        assign_student_form = AssignStudentToClassAndSubjectsForm(request.POST, school=school)  # Pass the school instance to the form

        if 'profile_image_submit' in request.POST:
            profile_image_form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_image_form.is_valid():
                profile_image_form.save()
                messages.success(request, 'Profile image updated successfully!')
                return redirect('user_management:school-admin-dashboard')

        if 'school_submit' in request.POST:
            # Make sure to include request.FILES for file upload handling
            school_form = SchoolForm(request.POST, request.FILES)
            if school_form.is_valid():
                school_form.save()
                messages.success(request, 'School updated successfully!')
                return redirect('user_management:school-admin-dashboard')
            else:
                # If the form is not valid, you would want to provide feedback
                messages.error(request, 'An error occurred while updating the school.')
        
        elif 'class_submit' in request.POST:
            if class_form.is_valid():
                class_instance = class_form.save(commit=False)
                class_instance.school = request.user.school_admin.school
                class_instance.save()
                messages.success(request, 'Class created successfully!')
                return redirect('user_management:school-admin-dashboard')
        
        elif 'subject_submit' in request.POST:
            if subject_form.is_valid():
                subject_form.save()
                messages.success(request, 'Subject created successfully!')
                return redirect('user_management:school-admin-dashboard')

        elif 'approve_enrollment_submit' in request.POST:
            if 'approve_enrollment_submit' in request.POST:
                enrollment_request_id = request.POST.get('enrollment_request_id')
                try:
                    enrollment_request = EnrollmentRequest.objects.get(pk=enrollment_request_id, school=school)
                    action = request.POST.get('action')
                    if action == 'approve':
                        enrollment_request.is_approved = True
                    elif action == 'reject':
                        enrollment_request.is_approved = False
                    enrollment_request.save()

                    # Handle approval logic if needed, such as updating the related teacher or student

                    messages.success(request, f'Enrollment request has been {action}d.')
                    return redirect('user_management:school-admin-dashboard')
                except EnrollmentRequest.DoesNotExist:
                    # Handle error here, maybe redirect to an error page
                    return redirect('error_page')
        
        elif 'assign_teacher_submit' in request.POST:
            if assign_teacher_form.is_valid():
                teacher = assign_teacher_form.cleaned_data['teacher']
                classes = assign_teacher_form.cleaned_data['classes']
                teacher.classes.add(classes)
                messages.success(request, 'Teacher assigned to class successfully!')
                return redirect('user_management:school-admin-dashboard')
            
        elif 'assign_student_submit' in request.POST:
            if assign_student_form.is_valid():
                student = assign_student_form.cleaned_data['student']
                class_obj = assign_student_form.cleaned_data['class_obj']
                subjects = assign_student_form.cleaned_data['subjects']

                # Assign the student to the class and the subjects
                student.enrolled_class = class_obj
                student.save()

                subject_combination, created = SubjectCombination.objects.get_or_create(student=student)
                subject_combination.subjects.set(subjects)

                messages.success(request, 'Student assigned to class and subjects successfully!')
                return redirect('user_management:school-admin-dashboard')
            
       # Handling bulk approval/rejection
        selected_requests = request.POST.getlist('selected_requests')
        action = request.POST.get('action')
        if selected_requests and action in ['approve', 'reject']:
            is_approved = True if action == 'approve' else False
            selected_enrollment_requests = EnrollmentRequest.objects.filter(pk__in=selected_requests, school=request.user.school_admin.school)

            # Iterate through the selected enrollment requests and update the related teacher's and student's status
            for request_obj in selected_enrollment_requests:
                if request_obj.teacher:
                    request_obj.teacher.is_approved = is_approved
                    request_obj.teacher.save()
                # If it's a student's request, update the student's status
                if request_obj.student:
                    request_obj.student.is_approved = is_approved
                    request_obj.student.save()

                request_obj.is_approved = is_approved
                request_obj.save()

            messages.success(request, f'Enrollment requests have been {action}d.')
            return redirect('user_management:school-admin-dashboard')

        # Fetch teachers and students related to the school
        teachers = Teacher.objects.filter(user__school=school, is_approved=True)
        students = Student.objects.filter(user__school=school)

        # Fetch unique classroom IDs that have a leaderboard entry
        class_ids = Leaderboard.objects.filter(classroom__in=school.classes.all()).values_list('classroom', flat=True).distinct()
        
        # Fetch the corresponding Leaderboard objects
        class_leaderboards = Leaderboard.objects.filter(classroom__in=class_ids)

        # Fetch unique subject IDs that have a leaderboard entry
        subject_ids = Leaderboard.objects.filter(subject__in=Subject.objects.filter(class_related__in=school.classes.all())).values_list('subject', flat=True).distinct()

        # Fetch the corresponding Leaderboard objects
        subject_leaderboards = Leaderboard.objects.filter(subject__in=subject_ids)

        # Fetch pending enrollment requests for the school admin
        pending_requests = EnrollmentRequest.objects.filter(school=request.user.school_admin.school, is_approved=None)
        # Handling bulk approval/rejection
        selected_requests = request.POST.getlist('selected_requests')
        action = request.POST.get('action')
        if selected_requests and action in ['approve', 'reject']:
            is_approved = True if action == 'approve' else False
            selected_enrollment_requests = EnrollmentRequest.objects.filter(pk__in=selected_requests, school=request.user.school_admin.school)

            # Iterate through the selected enrollment requests and update the related teacher's and student's status
            for request_obj in selected_enrollment_requests:
                if request_obj.teacher:
                    request_obj.teacher.is_approved = is_approved
                    request_obj.teacher.save()
                # If it's a student's request, update the student's status
                if request_obj.student:
                    request_obj.student.is_approved = is_approved
                    request_obj.student.save()

                request_obj.is_approved = is_approved
                request_obj.save()

            messages.success(request, f'Enrollment requests have been {action}d.')
            return redirect('user_management:school-admin-dashboard')
        
        return render(request, 'user_management/school_admin_dashboard.html', 
                    {'school_form': school_form, 
                    'class_form': class_form, 
                    'profile_image_form': profile_image_form,
                    'subject_form': subject_form, 
                    'assign_teacher_form': assign_teacher_form,
                    'assign_student_form': assign_student_form,
                    'class_leaderboards': class_leaderboards,
                    'subject_leaderboards': subject_leaderboards,
                    'teachers': teachers,
                    'students': students,
                    'pending_requests': pending_requests})  
    
class TeacherDashboardView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        teacher = request.user.teacher
        school = request.user.school  # Get school from user
        assigned_classes = teacher.classes.all()
        subjects = teacher.subjects.all()
        topic_form = TopicForm(teacher=teacher)
        subtopic_form = SubTopicForm(teacher=teacher)
        exam_form = ExamForm(request=request)
        questions_form = QuestionsForm(request=request)
        media_form = MediaForm()
        exams = Exam.objects.filter(is_published=False, teacher=teacher)
        published_exams = Exam.objects.filter(is_published=True, teacher=teacher)
        media_items = Media.objects.filter(school=school)  # Filter media by school

        # Fetch the Leaderboard entries related to the subjects the teacher is responsible for
        subject_leaderboards = Leaderboard.objects.filter(subject__in=subjects)
        profile_image = request.user.profile_image.url if request.user.profile_image else None
        profile_image_form = ProfileImageUpdateForm(instance=request.user)
        student_performance_form = StudentPerformanceForm(teacher=teacher)
        student_activity_form = StudentActivityForm(teacher=teacher)
        behavioral_assessment_form = BehavioralAssessmentForm(teacher=teacher)
        # Fetching all students in the teacher's classes
        assigned_classes_ids = teacher.classes.values_list('id', flat=True)
        students = Student.objects.filter(enrolled_class_id__in=assigned_classes_ids)

        # Fetching performances for the fetched students in the subjects taught by the teacher
        subjects_ids = teacher.subjects.values_list('id', flat=True)
        assigned_classes_ids = teacher.classes.values_list('id', flat=True)
        students = Student.objects.filter(enrolled_class_id__in=assigned_classes_ids)
        performances = Performance.objects.filter()
            

        return render(request, 'user_management/teacher_dashboard.html', {
            'classes': assigned_classes,
            'subjects': subjects,
            'topic_form': topic_form,
            'subtopic_form': subtopic_form,
            'exam_form': exam_form,
            'questions_form': questions_form,
            'media_form': media_form,
            'media_items': media_items,
            'exams': exams,
            'published_exams': published_exams,
            'subject_leaderboards': subject_leaderboards,  # Add this line to include leaderboard data
            'profile_image': profile_image,
            'profile_image_form': profile_image_form,
            'student_performance_form': student_performance_form,
            'student_activity_form': student_activity_form,
            'behavioral_assessment_form': behavioral_assessment_form,
            'manual_score_entry_url': reverse('exam_management:enter_manual_score'),
            'performances': performances,
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        teacher = request.user.teacher
        school = request.user.school
       # Initialize forms at the start
        topic_form = TopicForm(request.POST or None, teacher=teacher)
        subtopic_form = SubTopicForm(request.POST or None, teacher=teacher)
        exam_form = ExamForm(request.POST or None, request=request)
        questions_form = QuestionsForm(request.POST or None, request=request)
        media_form = MediaForm(request.POST, request.FILES)
        student_performance_form = StudentPerformanceForm(teacher=teacher)
        student_activity_form = StudentActivityForm(teacher=teacher)
        behavioral_assessment_form = BehavioralAssessmentForm(teacher=teacher)
        profile_image_form = ProfileImageUpdateForm(request.POST or None, request.FILES or None, instance=request.user)


        if 'student_performance_submit' in request.POST:
            student_performance_form = StudentPerformanceForm(data=request.POST, teacher=teacher)
            if student_performance_form.is_valid():
                student_performance_form.save()
                messages.success(request, 'Student performance saved successfully.')
                return redirect('user_management:teacher-dashboard')
        else:
            student_performance_form = StudentPerformanceForm(teacher=teacher)


        # Handle StudentActivity form submission
        if 'student_activity_submit' in request.POST:
            student_activity_form = StudentActivityForm(data=request.POST, teacher=teacher)
            if student_activity_form.is_valid():
                student_activity_form.save()
                messages.success(request, 'Student activity saved successfully.')
                return redirect('user_management:teacher-dashboard')
        else:
            student_activity_form = StudentActivityForm(teacher=teacher)

        # Handle BehavioralAssessment form submission
        if 'behavioral_assessment_submit' in request.POST:
            behavioral_assessment_form = BehavioralAssessmentForm(data=request.POST, teacher=teacher)
            if behavioral_assessment_form.is_valid():
                behavioral_assessment_form.save()
                messages.success(request, 'Behavioral assessment saved successfully.')
                return redirect('user_management:teacher-dashboard')
        else:
            behavioral_assessment_form = BehavioralAssessmentForm(teacher=teacher)

        if 'profile_image_submit' in request.POST:
            if profile_image_form.is_valid():
                profile_image_form.save()
                messages.success(request, 'Profile image updated successfully!')
                return redirect('user_management:teacher-dashboard')

        if 'topic_submit' in request.POST:
            if topic_form.is_valid():
                topic = topic_form.save()
                messages.success(request, 'Topic created successfully.')
                return redirect('user_management:teacher-dashboard')

        elif 'subtopic_submit' in request.POST:
            if subtopic_form.is_valid():
                subtopic = subtopic_form.save()
                messages.success(request, 'Subtopic created successfully.')
                return redirect('user_management:teacher-dashboard')

        elif 'exam_submit' in request.POST:
            if exam_form.is_valid():
                exam = exam_form.save(commit=False)
                exam.school = school
                exam.teacher = teacher
                exam.save()  # This should now correctly handle the category
                messages.success(request, 'Exam created successfully.')
                return redirect('user_management:teacher-dashboard')

        elif 'questions_submit' in request.POST:
            if questions_form.is_valid():
                question = questions_form.save(commit=False)
                question.school = request.user.school
                question.exam_id = request.session.get('current_exam_id')  # get current exam id from session
                question.save()
                messages.success(request, 'Question added successfully.')
                return redirect('user_management:teacher-dashboard')
            
        # Add this section for handling media uploads
        elif 'media_submit' in request.POST:
            media_form = MediaForm(request.POST, request.FILES)
            if media_form.is_valid():
                media = media_form.save(commit=False)
                media.school = request.user.school
                media.save()
                messages.success(request, 'Media uploaded successfully.')
                return redirect('user_management:teacher-dashboard')

        exams = Exam.objects.filter(is_published=False, subject__teachers=teacher)  # get unpublished exams

        return render(request, 'user_management/teacher_dashboard.html', {
            'subjects': teacher.subjects.all(),
            'topic_form': topic_form,
            'subtopic_form': subtopic_form,
            'exam_form': exam_form,
            'profile_image_form': profile_image_form,
            'student_performance_form': student_performance_form,
            'student_activity_form': student_activity_form,
            'behavioral_assessment_form': behavioral_assessment_form,
            'questions_form': questions_form,
            'exams': exams,  # add exams to the context
        })
    
@login_required
def publish_exam(request, exam_id):
    # Make sure the user is a teacher
    if not hasattr(request.user, 'teacher'):
        return render(request, 'error.html', {'message': 'Only teachers can publish exams.'})

    # Get the exam
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Check if the teacher of this exam is the one who's trying to publish it
    if exam.teacher != request.user.teacher:
        return render(request, 'error.html', {'message': 'You can only publish your own exams.'})

    # Publish the exam
    exam.is_published = True
    exam.save()

    messages.success(request, 'Exam published successfully.')
    
    # Redirect to teacher dashboard
    return HttpResponseRedirect(reverse('user_management:teacher-dashboard'))



class StudentDashboardView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        student = Student.objects.get(user=user)
        school = user.school

        # Get subjects related to the student's school
        subjects_for_school = Subject.objects.filter(class_related__school=school)

        try:
            subject_combination = student.subject_combination
            subjects = subject_combination.subjects.filter(class_related__school=school)
            subject_selection_form = SubjectSelectionForm(instance=subject_combination)
        except Student.subject_combination.RelatedObjectDoesNotExist:
            subjects = subjects_for_school
            subject_selection_form = SubjectSelectionForm()

        # Ensuring the form's subjects field only includes subjects related to the student's school
        subject_selection_form.fields['subjects'].queryset = subjects_for_school

        # Get all published exams for the student's subjects and school
        available_exams = Exam.objects.filter(
            is_published=True,
            subject__in=subjects,
            school=school
        ).select_related('category').order_by('category')  # Make sure to retrieve category data

        # Group exams by category
        categories_with_exams = {}
        for exam in available_exams:
            category = exam.category
            if category not in categories_with_exams:
                categories_with_exams[category] = []
            categories_with_exams[category].append(exam)
        # Get distinct categories
        categories = ExamCategory.objects.values_list('category_type', flat=True).distinct()


        student_exams = StudentExam.objects.filter(student=student)
        student_exam_answers = StudentExamAnswer.objects.filter(student_exam__in=student_exams)
        media_files = Media.objects.filter(school=school)
        media_items = Media.objects.filter(school=request.user.school)

        # Fetch leaderboard entries related to this student
        student_leaderboards = Leaderboard.objects.filter(student=student)

        # Fetch leaderboard entries related to the subjects the student is enrolled in
        subject_leaderboards = Leaderboard.objects.filter(subject__in=subjects)
        profile_image = request.user.profile_image.url if request.user.profile_image else None
        profile_image_form = ProfileImageUpdateForm(instance=request.user)

        # Get the latest exam attempt for this student
        latest_exam_attempt = ExamAttempt.objects.filter(student_exam__student=student).last()


        # If there is an exam attempt, generate the analysis
        if latest_exam_attempt:
            exam_analysis = generate_exam_analysis(latest_exam_attempt)
        else:
            exam_analysis = None

        return render(request, 'user_management/student_dashboard.html', {
            'categories_with_exams': categories_with_exams,
            'categories': categories,
            'available_exams': available_exams,
            'subjects': subjects,
            'subject_selection_form': subject_selection_form,
            'student_exams': student_exams,
            'student_exam_answers': student_exam_answers,
            'media_files': media_files,
            'media_items': media_items,
            'student_leaderboards': student_leaderboards,
            'subject_leaderboards': subject_leaderboards,
            'profile_image': profile_image,
            'profile_image_form': profile_image_form,
            'exam_analysis': exam_analysis  # Add this line to include the exam analysis in the template
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        student = Student.objects.get(user=user)

        try:
            subject_combination = student.subject_combination
        except Student.subject_combination.RelatedObjectDoesNotExist:
            subject_combination = SubjectCombination.objects.create(student=student)

        subject_selection_form = SubjectSelectionForm(request.POST, instance=subject_combination)

        if subject_selection_form.is_valid():
            subject_selection_form.save()
            messages.success(request, 'Subjects updated successfully!')

        if 'profile_image_submit' in request.POST:
            profile_image_form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_image_form.is_valid():
                profile_image_form.save()
                messages.success(request, 'Profile image updated successfully!')
                return redirect('user_management:student-dashboard')


        subjects = subject_combination.subjects.all()
        taken_exams = StudentExam.objects.filter(student=student).values_list('exam', flat=True)
        school = user.school
        exams = Exam.objects.exclude(id__in=taken_exams).filter(is_published=True, subject__in=subjects, school=school)

        return render(request, 'user_management/student_dashboard.html', {
            'exams': exams,
            'subjects': subjects,
            'subject_selection_form': subject_selection_form,
            'profile_image_form': profile_image_form,
        })

    

class AdminDashboardView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'user_management/admin_dashboard.html')
    
class IndependentLearnerDashboardView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)

        # Get all published global exams and group them by category
        available_global_exams = Exam.objects.filter(
            is_published=True,
            is_global=True
        ).select_related('category').order_by('category__category_type', 'category__name', 'category__year')

        # Group global exams by category
        categories_with_global_exams = {}
        for exam in available_global_exams:
            category_key = (exam.category.category_type, exam.category.name, exam.category.year)
            if category_key not in categories_with_global_exams:
                categories_with_global_exams[category_key] = []
            categories_with_global_exams[category_key].append(exam)

        # Get all global media
        available_global_media = Media.objects.filter(is_global=True)

        # Optionally, you may filter exams based on previous attempts by the independent learner
        independent_learner_attempts = ExamAttempt.objects.filter(student_exam__student__user=user)
        independent_learner_exams = [attempt.student_exam.exam for attempt in independent_learner_attempts]
        profile_image = request.user.profile_image.url if request.user.profile_image else None
        profile_image_form = ProfileImageUpdateForm(instance=request.user)


        # Get the latest exam attempt for this independent learner
        latest_exam_attempt = independent_learner_attempts.last()

        # If there is an exam attempt, generate the analysis
        if latest_exam_attempt:
            exam_analysis = generate_exam_analysis(latest_exam_attempt)
        else:
            exam_analysis = None

        return render(request, 'user_management/independent_learner_dashboard.html', {
            'categories_with_global_exams': categories_with_global_exams,
            'available_global_exams': available_global_exams,
            'independent_learner_exams': independent_learner_exams,
            'profile_image': profile_image,
            'profile_image_form': profile_image_form,
            'available_global_media': available_global_media,
            'exam_analysis': exam_analysis  # Add this line to include the exam analysis in the template
        })
    
    def post(self, request, *args, **kwargs):
        profile_image_form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
        if profile_image_form.is_valid():
            profile_image_form.save()
            messages.success(request, 'Profile image updated successfully!')
            return redirect('user_management:independent_learner_dashboard')

        # Re-render the page with the form containing errors
        return render(request, 'user_management/independent_learner_dashboard.html', {
            # Repopulate all other necessary context variables
            'profile_image_form': profile_image_form,
            # ... other context variables as in the GET method ...
        })
    
def video_tour(request):
    video_urls = [
        'https://www.youtube.com/embed/aQ5p3bL8-KQ',
        'https://www.youtube.com/embed/6juup7o1vGM',
        'https://www.youtube.com/embed/NnATHx84MyQ',
        'https://www.youtube.com/embed/K4wEpJVxmoY',
        'https://www.youtube.com/embed/DgZL3Pim8B4'
    ]
    return render(request, 'user_management/video_tour.html', {'video_urls': video_urls}) 