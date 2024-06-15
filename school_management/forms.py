# forms.py
from django import forms
from .models import School

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'address', 'logo', 'description']  # Include 'logo' and 'description' fields
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),  # Provide a larger textarea for description
        }