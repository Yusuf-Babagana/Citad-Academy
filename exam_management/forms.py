# exam_management/forms.py
from django import forms
from .models import Exam, Questions, Option, ExamCategory
from class_management.models import Subject
from subject_management.models import Topic, SubTopic
from django.forms import ModelForm, inlineformset_factory
from datetime import timedelta
from django.core.validators import RegexValidator
from student_management.models import StudentExamAnswer
from .models import ManualScore
from markdownx.fields import MarkdownxFormField  # Import MarkdownxFormField
from ckeditor.widgets import CKEditorWidget
from tinymce.widgets import TinyMCE

class ExamForm(forms.ModelForm):
    # Fields for creating a new category
    category = forms.ModelChoiceField(
        queryset=ExamCategory.objects.all(),
        required=False,
        empty_label="Create New Category"
    )
    new_category_name = forms.CharField(max_length=255, required=False)
    new_category_year = forms.IntegerField(required=False)
    category_type = forms.ChoiceField(choices=ExamCategory.CATEGORY_CHOICES, required=False)

    duration = forms.CharField(
        validators=[RegexValidator(r'^\d{1,3}(:[0-5]\d)?$', 'Enter a valid duration in the format "minutes" or "hours:minutes".')],
        label='Duration',
        help_text='Enter the duration in minutes or use the format "hours:minutes".',
        required=True
    )

    class Meta:
        model = Exam
        fields = ['subject', 'name', 'number_of_questions', 'duration', 'is_published', 'is_global', 'category']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ExamForm, self).__init__(*args, **kwargs)

        # Initialize subject queryset
        self.fields['subject'].queryset = Subject.objects.filter(teachers=self.request.user.teacher)

        # Get current choices from the ModelChoiceField and convert to list
        current_choices = list(self.fields['category'].choices)

        # Append the 'new' option
        current_choices.append(('new', 'Create New Category'))

        # Reassign the choices to include the 'new' option
        self.fields['category'].choices = current_choices

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if ':' in duration:
            hours, minutes = map(int, duration.split(':'))
            duration = timedelta(hours=hours, minutes=minutes)
        else:
            duration = timedelta(minutes=int(duration))
        return duration

    def clean(self):
        cleaned_data = super(ExamForm, self).clean()
        category = cleaned_data.get('category')

        if category is None:
            new_category_name = cleaned_data.get('new_category_name')
            new_category_year = cleaned_data.get('new_category_year')

            if not new_category_name:
                self.add_error('new_category_name', 'This field is required for a new category.')

            existing_category = ExamCategory.objects.filter(
                name=new_category_name, 
                year=new_category_year
            ).first()

            if existing_category:
                cleaned_data['category'] = existing_category

        return cleaned_data
    
    def is_valid(self):
        valid = super(ExamForm, self).is_valid()

        if self.cleaned_data.get('category') is None:
            new_category_name = self.cleaned_data.get('new_category_name')

            if not new_category_name:
                self.add_error('new_category_name', 'Please enter a name for the new category.')
                valid = False

        return valid

    def save(self, commit=True):
        if self.cleaned_data.get('category') is None and self.cleaned_data.get('new_category_name'):
            # Use the selected category type when creating a new category
            new_category = ExamCategory.objects.create(
                category_type=self.cleaned_data['category_type'],
                name=self.cleaned_data['new_category_name'],
                year=self.cleaned_data.get('new_category_year')
            )
            self.instance.category = new_category
        # No need for an else block, as the category is already set by the form field

        # Assign other fields if necessary before saving
        return super(ExamForm, self).save(commit=commit)

class QuestionsForm(forms.ModelForm):
    instructions = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)
    question_text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    explanation = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)

    class Meta:
        model = Questions
        fields = ['instructions', 'question_text', 'topic', 'subtopic', 'exam', 'explanation', 'question_image', 'question_pdf']

    question_image = forms.ImageField(required=False)
    question_pdf = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(QuestionsForm, self).__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.filter(subject__teachers=self.request.user.teacher)
        self.fields['subtopic'].queryset = SubTopic.objects.filter(topic__subject__teachers=self.request.user.teacher)
        self.fields['exam'].queryset = Exam.objects.filter(subject__teachers=self.request.user.teacher)

class OptionsForm(forms.ModelForm):
    option_text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Option
        fields = ['option_text', 'is_correct']

OptionsFormSet = forms.inlineformset_factory(Questions, Option, form=OptionsForm, extra=4, max_num=4, min_num=4)

class StudentExamAttemptForm(forms.ModelForm):
    selected_option = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, required=False)

    class Meta:
        model = StudentExamAnswer
        fields = ['selected_option']

    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            self.fields['selected_option'].queryset = Option.objects.filter(question=question)

class UploadQuestionsForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.csv'}))
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)
    exam = forms.ModelChoiceField(queryset=Exam.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")  # Get the logged-in user (teacher)
        super().__init__(*args, **kwargs)

        # Filtering the subjects and exams based on the logged-in teacher
        self.fields['subject'].queryset = Subject.objects.filter(teachers=self.user.teacher)
        self.fields['exam'].queryset = Exam.objects.filter(teacher=self.user.teacher)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1]  # Get the file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'csv']
            if ext.lower() not in allowed_extensions:
                raise forms.ValidationError('This file type is not supported.')
            if ext.lower() == 'docx' and file.size > 42 * 1024 * 1024:
                raise forms.ValidationError('The .docx file is too large ( > 42MB ).')
        return file
    
class ManualScoreForm(forms.ModelForm):
    class Meta:
        model = ManualScore
        fields = ['student', 'subject', 'teacher', 'ca1_score', 'ca2_score', 'exam_score', 'total_score', 'date_assigned']