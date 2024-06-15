from django import forms
from .models import Resource, Comment, ResourceComment

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'slug', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        # Implement save functionality if needed, such as sending an email
        pass


class ResourceCommentForm(forms.ModelForm):
    class Meta:
        model = ResourceComment
        fields = ['comment', 'name', 'email']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'comment': 'Add a comment',
            'name': 'Name',
            'email': 'Email',
        }

    def __init__(self, *args, **kwargs):
        # Extract 'user' from kwargs with a default of None if not present
        user = kwargs.pop('user', None)
        super(ResourceCommentForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            # Hide name and email fields for authenticated users
            del self.fields['name']
            del self.fields['email']