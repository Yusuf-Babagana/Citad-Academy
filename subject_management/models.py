#subject_management
from django.db import models
from class_management.models import Subject

class Topic(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name

class SubTopic(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')

    def __str__(self):
        return self.name
