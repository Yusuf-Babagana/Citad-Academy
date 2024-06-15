#class_management app
from django.db import models
from user_management.models import User
from school_management.models import School

class Class(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    classes = models.ManyToManyField(Class, related_name='teachers')
    is_approved = models.BooleanField(default=False)  # Added approval field
    field_of_study = models.CharField(max_length=100)

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}' if self.user.first_name and self.user.last_name else self.user.username
        return f'{full_name} - Field of Study: {self.field_of_study}'

class Subject(models.Model):
    name = models.CharField(max_length=255)
    class_related = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teachers = models.ManyToManyField(Teacher, related_name='subjects')  # new

    def __str__(self):
        return self.name
