from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Topic, SubTopic
from .serializers import TopicSerializer, SubTopicSerializer

class TopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubTopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        subtopics = SubTopic.objects.all()
        serializer = SubTopicSerializer(subtopics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
