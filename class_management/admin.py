from django.contrib import admin
from .models import Class, Teacher, Subject  # Add your model names here

admin.site.register(Class)
admin.site.register(Teacher)
admin.site.register(Subject)
