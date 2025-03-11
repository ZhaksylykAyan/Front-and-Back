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

    def perform_create(self, serializer):
        """ Assigns the correct creator and auto-creates a team. """
        user = self.request.user

        if hasattr(user, 'student_profile'):
            if ThesisTopic.objects.filter(created_by_student=user.student_profile).exists():
                raise ValidationError("Students can only create one thesis topic.")
            thesis_topic = serializer.save(created_by_student=user.student_profile)

        elif hasattr(user, 'supervisor_profile'):
            if ThesisTopic.objects.filter(created_by_supervisor=user.supervisor_profile).count() >= 10:
                raise ValidationError("Supervisors can create up to 10 thesis topics.")
            thesis_topic = serializer.save(created_by_supervisor=user.supervisor_profile)

        else:
            raise ValidationError("Only students and supervisors can create a thesis topic.")

        # Auto-create a team with the creator as the owner
        Team.objects.create(
            thesis_topic=thesis_topic,
            owner=user,
            status="open"
        )


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