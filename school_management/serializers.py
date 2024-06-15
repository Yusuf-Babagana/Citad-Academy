# school_management/serializers.py
from rest_framework import serializers
from .models import School, SchoolAdmin
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'address', 'logo', 'description']

class SchoolAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = SchoolAdmin
        fields = ['username', 'email', 'school']

class SchoolUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name', 'address', 'logo', 'description']

    def save(self, **kwargs):
        logo = self.validated_data.get('logo', None)
        
        # Check if a new logo file has been uploaded
        if logo and isinstance(logo, InMemoryUploadedFile):
            # Save the new logo file to the school instance
            self.instance.logo.save(logo.name, logo, save=False)
        
        # Call the superclass's save method to handle saving other fields
        return super().save(**kwargs)