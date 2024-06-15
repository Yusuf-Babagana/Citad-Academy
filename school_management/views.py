from django.shortcuts import render
from rest_framework import generics
from .models import School, SchoolAdmin
from .serializers import SchoolSerializer, SchoolAdminSerializer

class SchoolList(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class SchoolDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class SchoolAdminList(generics.ListCreateAPIView):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer

class SchoolAdminDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer

# new view to serve the template
def index(request):
    return render(request, 'school_management/index.html')
