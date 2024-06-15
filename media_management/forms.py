#media_management/forms.py
from django import forms
from .models import Media, Comment, CategoryType, CategoryDetail

class MediaForm(forms.ModelForm):
    # Additional fields for category creation
    category_type = forms.ModelChoiceField(
        queryset=CategoryType.objects.all(),
        required=False,
        label='Category Type'
    )
    category_detail = forms.ModelChoiceField(
        queryset=CategoryDetail.objects.none(),  # Initially empty
        required=False,
        label='Category Detail'
    )
    new_category_type = forms.CharField(max_length=255, required=False, label='New Category Type')
    new_category_detail = forms.CharField(max_length=255, required=False, label='New Category Detail')

    class Meta:
        model = Media
        fields = ['title', 'file', 'file_type', 'is_global']  # Do not include category_type and category_detail here

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)
        # Initial queryset settings for category_type and category_detail

    def save(self, commit=True):
        media = super().save(commit=False)

        # Handle category detail
        category_detail_id = self.cleaned_data.get('category_detail')
        if category_detail_id:
            media.category_detail = CategoryDetail.objects.get(id=category_detail_id)
        else:
            # Handle the creation of new category type and detail
            new_category_type_name = self.cleaned_data.get('new_category_type')
            new_category_detail_name = self.cleaned_data.get('new_category_detail')
            if new_category_type_name and new_category_detail_name:
                category_type, _ = CategoryType.objects.get_or_create(name=new_category_type_name)
                category_detail, _ = CategoryDetail.objects.get_or_create(name=new_category_detail_name, category_type=category_type)
                media.category_detail = category_detail

        if commit:
            media.save()
        return media

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
