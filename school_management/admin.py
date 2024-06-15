from django.contrib import admin
from .models import School, SchoolAdmin  # Add your model names here

admin.site.register(School)
admin.site.register(SchoolAdmin)
