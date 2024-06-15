# class_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Class
from .serializers import ClassSerializer, TeacherSerializer, SubjectSerializer
from .forms import ClassForm, SubjectForm
from .models import Teacher
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class ClassList(generics.ListCreateAPIView):
    serializer_class = ClassSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'SA':
            return Class.objects.filter(school=self.request.user.school)
        elif self.request.user.role == 'T' and hasattr(self.request.user, 'teacher'):
            return self.request.user.teacher.classes.all()
        elif self.request.user.role == 'S' and hasattr(self.request.user, 'student'):
            return Class.objects.filter(id=self.request.user.student.enrolled_class.id)
        return Class.objects.none()

class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'SA':
            return Class.objects.filter(school=self.request.user.school)
        elif self.request.user.role == 'T' and hasattr(self.request.user, 'teacher'):
            return self.request.user.teacher.classes.all()
        elif self.request.user.role == 'S' and hasattr(self.request.user, 'student'):
            return Class.objects.filter(id=self.request.user.student.enrolled_class.id)
        return Class.objects.none()
    
class ClassesBySchool(generics.ListAPIView):
    serializer_class = ClassSerializer

    def get_queryset(self):
        school_id = self.kwargs['school_id']
        return Class.objects.filter(school_id=school_id)

class TeacherListAPIView(APIView):
    def get(self, request, format=None):
        if self.request.user.role in ['SA', 'T', 'S'] and self.request.user.school is not None:
            teachers = Teacher.objects.filter(user__school=self.request.user.school)
            serializer = TeacherSerializer(teachers, many=True)
            return Response(serializer.data)
        return Response({"error": "Not allowed or missing school information"}, status=400)

class AssignTeacherAPIView(APIView):
    def post(self, request, format=None):
        teacher_id = request.data.get('teacher_id')
        class_id = request.data.get('class_id')

        # Get the teacher
        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Get the class
        class_instance = get_object_or_404(Class, id=class_id)

        # Check if the class belongs to the same school as the teacher
        if class_instance.school != teacher.user.school:
            return Response({"message": "The class and the teacher do not belong to the same school."}, status=status.HTTP_400_BAD_REQUEST)
        
        teacher.classes.add(class_id)
        
        return Response({"message": "Teacher assigned to class successfully!"}, status=status.HTTP_200_OK)

class ClassCreateView(View):
    @method_decorator(login_required(login_url='/user_management/login/'))
    def get(self, request, *args, **kwargs):
        form = ClassForm()
        return render(request, 'class_management/create_class.html', {'form': form})
    
    @method_decorator(login_required(login_url='/user_management/login/'))
    def post(self, request, *args, **kwargs):
        form = ClassForm(request.POST)
        if form.is_valid():
            class_instance = form.save(commit=False)
            class_instance.school = request.user.school_admin.school
            class_instance.save()
            return redirect('user_management:school-admin-dashboard')
        return render(request, 'class_management/create_class.html', {'form': form})
    
class SubjectCreateAPIView(APIView):
    @method_decorator(login_required(login_url='/user_management/login/'))
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectCreateView(View):
    @method_decorator(login_required(login_url='/user_management/login/'))
    def get(self, request, *args, **kwargs):
        form = SubjectForm()
        return render(request, 'class_management/create_subject.html', {'form': form})

    @method_decorator(login_required(login_url='/user_management/login/'))
    def post(self, request, *args, **kwargs):
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management:school-admin-dashboard')
        return render(request, 'class_management/create_subject.html', {'form': form})

def index(request):
    return render(request, 'class_management/index.html')
