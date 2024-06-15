from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Resource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='resources/')
    timestamp = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    file = models.FileField(upload_to='resources/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Resource, self).save(*args, **kwargs)

    
# Utility function, it could be inside models.py as a method of the Resource model
    def create_slug(title):
        return slugify(title)


class ResourceComment(models.Model):
    resource = models.ForeignKey(Resource, related_name='resource_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resource_comments', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)  # For anonymous users
    email = models.EmailField(null=True, blank=True)  # For anonymous users
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Comment by {self.user.username} on {self.resource.title}"
        else:
            return f"Comment by Anonymous ({self.name}) on {self.resource.title}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

# Assuming you need both Comment models to be distinct and serve different purposes
class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_comments')
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return f'Comment by {self.author} on {self.resource}'
