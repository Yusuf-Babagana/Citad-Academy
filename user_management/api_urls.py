from django.urls import path
from .api_views import SchoolAdminRegisterAPIView, TeacherRegisterAPIView, StudentRegisterAPIView, get_classes, IndependentLearnerRegisterAPIView, CustomTokenObtainPairView, SchoolAdminDashboardAPIView, UserProfileImageUpdateView
from . import api_views

app_name = 'user_management'

urlpatterns = [
    

    path('register/teacher/', TeacherRegisterAPIView.as_view(), name='api_register_teacher'),
    path('register/school_admin/', SchoolAdminRegisterAPIView.as_view(), name='api_register_school_admin'),
    path('register/student/', StudentRegisterAPIView.as_view(), name='api_register_student'),
    path('get_classes/', get_classes, name='api_get_classes'),
    path('register/independent_learner/', IndependentLearnerRegisterAPIView.as_view(), name='api_register_independent_learner'),
    path('login/', CustomTokenObtainPairView.as_view(), name='api_login'),
    path('school-admin-dashboard/', SchoolAdminDashboardAPIView.as_view(), name='school-admin-dashboard-api'),
    path('update-profile-image/', UserProfileImageUpdateView.as_view(), name='update-profile-image'),

    path('user/detail/', api_views.UserDetailView.as_view(), name='user-detail'),
    path('user/list/', api_views.UserListView.as_view(), name='user-list'),
    path('user/update/', api_views.UserUpdateView.as_view(), name='user-update'),
    path('user/role/update/<int:pk>/', api_views.UserRoleUpdateView.as_view(), name='user-role-update'),
]
