from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import (UserManagementIndexView, SchoolAdminRegisterView, TeacherRegisterView, 
                    StudentRegisterView, IndependentLearnerRegisterView, AdminRegisterView, LoginView, 
                    SchoolAdminDashboardView, TeacherDashboardView, StudentDashboardView, IndependentLearnerDashboardView,
                    AdminDashboardView, publish_exam, LogoutView, GetStartedView, TakeTourView)
from . import views


app_name = 'user_management'

urlpatterns = [
    path('', UserManagementIndexView.as_view(), name='index'),
    path('register/school_admin/', SchoolAdminRegisterView.as_view(), name='register_school_admin'),
    path('register/teacher/', TeacherRegisterView.as_view(), name='register_teacher'),
    path('register/student/', StudentRegisterView.as_view(), name='register_student'),
    path('get_classes/', views.get_classes, name='get_classes'),
    path('register_independent_learner/', IndependentLearnerRegisterView.as_view(), name='register_independent_learner'),
    path('register/admin/', AdminRegisterView.as_view(), name='register_admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get-started/', GetStartedView.as_view(), name='get_started'),
    path('take-tour/', TakeTourView.as_view(), name='take_tour'),
    path('school_admin_dashboard/', SchoolAdminDashboardView.as_view(), name='school-admin-dashboard'),
    path('teacher_dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('teacher_dashboard/publish_exam/<int:exam_id>/', publish_exam, name='publish-exam'),
    path('student_dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('independent_learner_dashboard/', IndependentLearnerDashboardView.as_view(), name='independent_learner_dashboard'),
    path('admin_dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('video-tour/', views.video_tour, name='video_tour'),
]
