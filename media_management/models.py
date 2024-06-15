#media_management.models
from django.db import models
from school_management.models import School
from user_management.models import User

# File Type Choices
FILE_TYPE_CHOICES = [
    ('image', 'Image'),
    ('video', 'Video'),
    ('text', 'Text'),
    ('pdf', 'PDF'),
    ('ppt', 'PowerPoint'),  # Add this line to handle PowerPoint files
]

class CategoryType(models.Model):
    name = models.CharField(max_length=255)  # e.g., University, WAEC

    def __str__(self):
        return self.name

class CategoryDetail(models.Model):
    category_type = models.ForeignKey(CategoryType, related_name='details', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # e.g., University of Amsterdam, Mathematics

    def __str__(self):
        return f"{self.category_type.name} - {self.name}"

class Media(models.Model):
    category_detail = models.ForeignKey(CategoryDetail, related_name='media_files', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)  # Make school optional
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='media_files/')
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
    )
    is_global = models.BooleanField(default=False)  # Add this line to indicate if the media is global

    def __str__(self):
        return self.title

class Comment(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50] + "..."
