from rest_framework import generics, permissions
from .models import ThesisTopic
from .serializers import ThesisTopicSerializer
from rest_framework.exceptions import PermissionDenied


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

class ThesisTopicUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ThesisTopic.objects.all()
    serializer_class = ThesisTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        # Проверка, что только owner может редактировать
        if hasattr(user, 'student_profile'):
            if obj.created_by_student != user.student_profile:
                raise PermissionDenied("You do not own this topic.")
        elif hasattr(user, 'supervisor_profile'):
            if obj.created_by_supervisor != user.supervisor_profile:
                raise PermissionDenied("You do not own this topic.")
        else:
            raise PermissionDenied("Invalid user.")

        return obj