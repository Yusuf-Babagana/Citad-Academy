from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SchoolAdminRegisterSerializer, IndependentLearnerRegisterSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import TeacherRegisterSerializer
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from class_management.models import Teacher, Class
from school_management.models import SchoolAdmin
from rest_framework.decorators import permission_classes
from .serializers import StudentRegisterSerializer
from django.db import transaction
from student_management.models import Student, EnrollmentRequest
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    UserRoleUpdateSerializer
)

User = get_user_model()

class SchoolAdminRegisterAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this endpoint.

    def post(self, request, *args, **kwargs):
        serializer = SchoolAdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Registration successful. You can now log in."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherRegisterAPIView(generics.GenericAPIView):
    serializer_class = TeacherRegisterSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated and has the right role.

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():  # Ensure atomicity of the database operation
                    # Pass the request object to serializer's save method to access user and their school
                    user = serializer.save(request=request)
                    return Response({'message': 'Registration successful. The teacher can now log in.'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "You don't have permission to access this page."}, status=status.HTTP_403_FORBIDDEN)
        
class StudentRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'SA':
            serializer = StudentRegisterSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()
                    return Response({'message': 'Registration successful. The student can now log in.'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "You don't have permission to access this page."}, status=status.HTTP_403_FORBIDDEN)

def get_classes(request):
    if not request.user.is_authenticated or request.user.role != 'SA':
        return JsonResponse({'error': "Unauthorized access"}, status=403)

    school_id = request.query_params.get('school_id', None)
    if school_id:
        classes = Class.objects.filter(school_id=school_id).values('id', 'name')
        class_list = list(classes)
        return JsonResponse({'classes': class_list})
    else:
        return JsonResponse({'classes': []})
    
class IndependentLearnerRegisterAPIView(APIView):
    permission_classes = [AllowAny]  # This endpoint is accessible without authentication.

    def post(self, request, *args, **kwargs):
        serializer = IndependentLearnerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Convert username to lowercase, set role, and trial period within serializer
            # Assuming these are handled in the serializer's save method now

            return Response({'message': 'Registration successful. You can now log in.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ApiLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRoleUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# user_management/api_views.py/schooladmindashboardview
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from school_management.models import School
from class_management.models import Class, Subject, Teacher
from student_management.models import Student, EnrollmentRequest
from leaderboard.models import Leaderboard
from school_management.serializers import SchoolSerializer
from class_management.serializers import TeacherSerializer
from student_management.serializers import StudentSerializer, EnrollmentRequestSerializer 
from leaderboard.serializers import LeaderboardSerializer 
from .serializers import UserProfileImageUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class SchoolAdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if user is a school admin
        if not hasattr(user, 'school_admin'):
            return Response({'error': 'User is not a school admin'}, status=403)

        school = user.school_admin.school

        teachers = Teacher.objects.filter(user__school=school, is_approved=True)
        students = Student.objects.filter(user__school=school)
        class_ids = Leaderboard.objects.filter(classroom__in=school.classes.all()).values_list('classroom', flat=True).distinct()
        class_leaderboards = Leaderboard.objects.filter(classroom__in=class_ids)
        subject_ids = Leaderboard.objects.filter(subject__in=Subject.objects.filter(class_related__in=school.classes.all())).values_list('subject', flat=True).distinct()
        subject_leaderboards = Leaderboard.objects.filter(subject__in=subject_ids)
        pending_requests = EnrollmentRequest.objects.filter(school=school, is_approved=None).select_related('student__user', 'teacher__user')

        # Ensure profile image URL is correctly formed, especially when using cloud storage or when MEDIA_URL is set
        profile_image_url = request.build_absolute_uri(user.profile_image.url) if user.profile_image else None

        dashboard_data = {
            'school': SchoolSerializer(school).data,
            'teachers': TeacherSerializer(teachers, many=True).data,
            'students': StudentSerializer(students, many=True).data,
            'class_leaderboards': LeaderboardSerializer(class_leaderboards, many=True).data,
            'subject_leaderboards': LeaderboardSerializer(subject_leaderboards, many=True).data,
            'pending_requests': EnrollmentRequestSerializer(pending_requests, many=True).data,
            'profile_image': profile_image_url,
        }

        return Response(dashboard_data)

class UserProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileImageUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile image updated successfully.'})
        else:
            return Response(serializer.errors, status=400)