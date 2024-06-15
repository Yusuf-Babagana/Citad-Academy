from django.contrib import admin
from django import forms
from .models import Exam, Questions, Option, ExamAttempt, ManualScore, ExamCategory
from ckeditor.widgets import CKEditorWidget
from tinymce.widgets import TinyMCE

class QuestionsAdminForm(forms.ModelForm):
    instructions = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)
    question_text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    explanation = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)

    class Meta:
        model = Questions
        fields = '__all__'

class QuestionsAdmin(admin.ModelAdmin):
    form = QuestionsAdminForm

class OptionAdminForm(forms.ModelForm):
    option_text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Option
        fields = '__all__'

class OptionAdmin(admin.ModelAdmin):
    form = OptionAdminForm

# Register your models with their respective ModelAdmin
admin.site.register(ExamCategory)
admin.site.register(Exam)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(ExamAttempt)
admin.site.register(ManualScore)
