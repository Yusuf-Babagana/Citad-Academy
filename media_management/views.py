#media_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Media, CategoryType, CategoryDetail
from .forms import MediaForm, CommentForm 
from .serializers import MediaSerializer
from django.contrib.auth.decorators import login_required


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

@login_required
def index(request):
    # Fetch all media related to the school of the logged in user
    media = Media.objects.filter(school=request.user.student.school)
    return render(request, 'media_management/index.html', {'media': media})


@login_required
def upload_media(request):
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media_item = form.save(commit=False)
            media_item.school = request.user.teacher.school  # Set the school of the media item to the school of the logged-in teacher
            
            # If you want to set the 'is_global' field based on the user role or some other logic, you can do it here. For example:
            # media_item.is_global = some_logic_to_determine_if_global
            
            media_item.save()
            return redirect('teacher_dashboard')
    else:
        form = MediaForm()
    return render(request, 'media_management/upload_media.html', {'form': form})

@login_required
def view_media(request, media_id):
    media_item = get_object_or_404(Media, pk=media_id)
    comments = media_item.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.media = media_item
            comment.user = request.user
            comment.save()
            return redirect('media_management:view_media', media_id=media_id)
    else:
        form = CommentForm()
    return render(request, 'media_management/view_media.html', {'media': media_item, 'comments': comments, 'form': form})

@login_required
def list_category_types(request):
    category_types = CategoryType.objects.all()
    return render(request, 'media_management/list_category_types.html', {'category_types': category_types})

@login_required
def list_category_details(request, category_type_id):
    category_type = CategoryType.objects.get(id=category_type_id)
    category_details = CategoryDetail.objects.filter(category_type=category_type)
    return render(request, 'media_management/list_category_details.html', {
        'category_type': category_type,
        'category_details': category_details
    })

@login_required
def list_media_files(request, category_detail_id):
    category_detail = CategoryDetail.objects.get(id=category_detail_id)
    media_files = Media.objects.filter(category_detail=category_detail)
    return render(request, 'media_management/list_media_files.html', {
        'category_detail': category_detail,
        'media_files': media_files
    })