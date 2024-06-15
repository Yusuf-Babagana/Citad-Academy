from django.contrib import admin
from .models import Resource  # Adjust the import path according to your app structure

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'timestamp', 'is_active')  # Customize as needed
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'timestamp')
    prepopulated_fields = {'slug': ('title',)}  # Automatically populate the slug field from the title

# If you have other related models like Comment, register them similarly.
