# student_management/forms.py
from django import forms
from class_management.models import Subject
from .models import (
    SubjectCombination,
    StudentExamAnswer,
    StudentPerformance,
    StudentActivity,
    BehavioralAssessment,
    Student,
)

class StudentPerformanceForm(forms.ModelForm):
    class Meta:
        model = StudentPerformance
        fields = ['student', 'subject', 'term', 'year', 'grade']

    def __init__(self, teacher=None, *args, **kwargs):
        super(StudentPerformanceForm, self).__init__(*args, **kwargs)
        if teacher:
            assigned_classes = teacher.classes.all()
            self.fields['student'].queryset = Student.objects.filter(enrolled_class__in=assigned_classes)

class StudentActivityForm(forms.ModelForm):
    class Meta:
        model = StudentActivity
        fields = ['student', 'activity_name', 'description', 'participation_level']

    def __init__(self, teacher=None, *args, **kwargs):
        super(StudentActivityForm, self).__init__(*args, **kwargs)
        if teacher:
            assigned_classes = teacher.classes.all()
            self.fields['student'].queryset = Student.objects.filter(enrolled_class__in=assigned_classes)

class BehavioralAssessmentForm(forms.ModelForm):
    class Meta:
        model = BehavioralAssessment
        fields = ['student', 'behavior', 'score', 'term', 'year']

    def __init__(self, teacher=None, *args, **kwargs):
        super(BehavioralAssessmentForm, self).__init__(*args, **kwargs)
        if teacher:
            assigned_classes = teacher.classes.all()
            self.fields['student'].queryset = Student.objects.filter(enrolled_class__in=assigned_classes)

class SubjectSelectionForm(forms.ModelForm):
    class Meta:
        model = SubjectCombination
        fields = ['subjects']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subjects'].queryset = Subject.objects.all()

            
class StudentExamAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentExamAnswer
        fields = ['student_answer']


class AnswerForm(forms.Form):
    CHOICES = [(i, f'Option {i}') for i in range(1, 5)]
    selected_option = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)