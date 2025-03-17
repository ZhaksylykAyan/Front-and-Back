from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ThesisTopic
from .serializers import ThesisTopicSerializer
from teams.models import Team
from django.core.exceptions import ValidationError


class ThesisTopicCreateView(generics.CreateAPIView):
    """ Allows students and supervisors to create a thesis topic. """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.IsAuthenticated]


class ThesisTopicListView(generics.ListAPIView):
    """ Lists all thesis topics. """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.AllowAny]


class ThesisTopicDetailView(generics.RetrieveAPIView):
    """ Retrieves a single thesis topic. """
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.AllowAny]