from rest_framework import generics
from .models import CategoryType, CategoryDetail, Media, Comment
from .serializers import CategoryTypeSerializer, CategoryDetailSerializer, MediaSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated

class CategoryTypeListView(generics.ListCreateAPIView):
    queryset = CategoryType.objects.all()
    serializer_class = CategoryTypeSerializer

class CategoryDetailListView(generics.ListCreateAPIView):
    queryset = CategoryDetail.objects.all()
    serializer_class = CategoryDetailSerializer

class MediaListView(generics.ListCreateAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]

class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]

class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
