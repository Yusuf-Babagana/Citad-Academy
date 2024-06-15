from django.contrib import admin
from .models import Topic, SubTopic  # Add your model names here

admin.site.register(Topic)
admin.site.register(SubTopic)
