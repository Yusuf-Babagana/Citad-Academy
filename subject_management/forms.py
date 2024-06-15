# subject_management/forms.py

from django import forms
from .models import Topic, SubTopic, Subject
from class_management.models import Teacher

class TopicForm(forms.ModelForm):
    # Subjects associated with the teacher
    subject = forms.ModelChoiceField(queryset=Subject.objects.none())

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher')
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(teachers=teacher)

    class Meta:
        model = Topic
        fields = ['name', 'subject']

class SubTopicForm(forms.ModelForm):
    # Topics associated with the teacher
    topic = forms.ModelChoiceField(queryset=Topic.objects.none())

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher')
        super(SubTopicForm, self).__init__(*args, **kwargs)
        subjects_of_teacher = Subject.objects.filter(teachers=teacher)
        self.fields['topic'].queryset = Topic.objects.filter(subject__in=subjects_of_teacher)

    class Meta:
        model = SubTopic
        fields = ['name', 'topic']
