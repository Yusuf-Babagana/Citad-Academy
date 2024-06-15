# class_management/forms.py
from django import forms
from .models import Class, Teacher, Subject 
from student_management.models import Student

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']

class AssignTeacherToClassForm(forms.Form):
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super(AssignTeacherToClassForm, self).__init__(*args, **kwargs)
        if school:
            self.fields['teacher'].queryset = Teacher.objects.filter(user__school=school, is_approved=True)
            self.fields['classes'].queryset = Class.objects.filter(school=school)

    teacher = forms.ModelChoiceField(queryset=Teacher.objects.none()) 
    classes = forms.ModelChoiceField(queryset=Class.objects.none())

class SubjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super(SubjectForm, self).__init__(*args, **kwargs)
        if school:
            self.fields['class_related'].queryset = Class.objects.filter(school=school)
            self.fields['teachers'].queryset = Teacher.objects.filter(user__school=school, is_approved=True)

    class_related = forms.ModelChoiceField(queryset=Class.objects.none())
    teachers = forms.ModelMultipleChoiceField(queryset=Teacher.objects.none())

    class Meta:
        model = Subject
        fields = ['name', 'class_related', 'teachers']

class AssignStudentToClassAndSubjectsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super(AssignStudentToClassAndSubjectsForm, self).__init__(*args, **kwargs)
        if school:
            self.fields['student'].queryset = Student.objects.filter(user__school=school)
            self.fields['class_obj'].queryset = Class.objects.filter(school=school)
            self.fields['subjects'].queryset = Subject.objects.filter(class_related__school=school)

    student = forms.ModelChoiceField(queryset=Student.objects.none())
    class_obj = forms.ModelChoiceField(queryset=Class.objects.none())
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.none())
