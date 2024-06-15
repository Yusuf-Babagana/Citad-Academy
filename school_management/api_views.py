from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import School, SchoolAdmin
from .serializers import SchoolSerializer, SchoolAdminSerializer, SchoolUpdateSerializer

class SchoolListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        schools = School.objects.all()
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SchoolDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        school = School.objects.get(pk=pk)
        serializer = SchoolSerializer(school)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SchoolAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        school_admins = SchoolAdmin.objects.all()
        serializer = SchoolAdminSerializer(school_admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SchoolUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        try:
            school = School.objects.get(pk=pk, admin__user=request.user)
        except School.DoesNotExist:
            return Response({"error": "School not found or not authorized."}, status=404)

        serializer = SchoolUpdateSerializer(school, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)