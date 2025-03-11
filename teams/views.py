from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from topics.models import ThesisTopic
from .models import Team
from .serializers import TeamSerializer
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification


def send_notification(user, message):
    """ Sends a notification to a user (DB + WebSocket) """
    Notification.objects.create(user=user, message=message)

    # Send real-time notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {"type": "send_notification", "message": message},
    )

class TeamCreateView(generics.CreateAPIView):
    """ Allows students and supervisors to create a team manually (not needed, as teams are auto-created). """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeamListView(generics.ListAPIView):
    """ Lists all teams. """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

class TeamDetailView(generics.RetrieveAPIView):
    """ Retrieves a single team. """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

class ApplyToSupervisorView(APIView):
    """ Allows a team to apply to a supervisor """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if team.status != "open":
                return Response({"error": "Team is not open for applications."}, status=status.HTTP_400_BAD_REQUEST)

            if not team.has_required_skills():
                return Response({"error": "Team does not meet the required skills."}, status=status.HTTP_400_BAD_REQUEST)

            team.status = "pending"
            team.save()

            # Notify Supervisor
            if team.thesis_topic.created_by_supervisor:
                send_notification(team.thesis_topic.created_by_supervisor.user, f"Team applied for '{team.thesis_topic.title}'")

            return Response({"message": "Application sent to supervisor."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

class ApproveTeamView(APIView):
    """ Allows a supervisor to approve a team """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if not hasattr(request.user, 'supervisor_profile'):
                return Response({"error": "Only supervisors can approve teams."}, status=status.HTTP_403_FORBIDDEN)

            total_owned = Team.objects.filter(owner=request.user).count() + ThesisTopic.objects.filter(
                created_by_supervisor=request.user.supervisor_profile).count()
            if total_owned >= 10:
                return Response(
                    {"error": "Supervisors cannot own more than 10 teams including thesis topics they created."},
                    status=status.HTTP_400_BAD_REQUEST)

            team.approve_team(request.user.supervisor_profile)

            # Notify students in the team
            for student in team.members.all():
                send_notification(student.user, f"Your team for '{team.thesis_topic.title}' was approved!")

            return Response({"message": "Team approved successfully."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

class RejectTeamView(APIView):
    """ Allows a supervisor to reject a team """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if not hasattr(request.user, 'supervisor_profile'):
                return Response({"error": "Only supervisors can reject teams."}, status=status.HTTP_403_FORBIDDEN)

            team.reject_team()

            # Notify students about rejection
            for student in team.members.all():
                send_notification(student.user, f"Your team for '{team.thesis_topic.title}' was rejected.")

            return Response({"message": "Team rejected successfully."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)