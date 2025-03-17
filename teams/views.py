from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from profiles.models import SupervisorProfile
from topics.models import ThesisTopic
from topics.serializers import ThesisTopicSerializer
from .models import Team, JoinRequest, SupervisorRequest
from .serializers import TeamSerializer, JoinRequestSerializer, SupervisorRequestSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



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


class MyTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = None
        if hasattr(user, "student_profile"):
            profile = user.student_profile
        elif hasattr(user, "supervisor_profile"):
            profile = user.supervisor_profile
        else:
            return Response({"detail": "No profile found"}, status=400)

        try:
            team = Team.objects.get(owner=request.user)
            serializer = TeamSerializer(team)
            data = serializer.data
            data['is_owner'] = True  # 💥 ВАЖНО
            return Response(data)

        except Team.DoesNotExist:
            # Если не owner, но студент — участник команды
            if hasattr(user, "student_profile"):
                try:
                    team = Team.objects.get(members=user.student_profile)
                    serializer = TeamSerializer(team)
                    data = serializer.data
                    data['is_owner'] = False
                    return Response(data)
                except Team.DoesNotExist:
                    return Response({"detail": "No team found"}, status=404)
            else:
                return Response({"detail": "No team found"}, status=404)

class SupervisorProjectsView(APIView):
    """Returns all supervisor's projects"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "supervisor_profile"):
            return Response({"error": "Only supervisors can access this."}, status=403)

        supervisor = request.user.supervisor_profile

        # 1. Темы, созданные супервизором
        created_topics = ThesisTopic.objects.filter(created_by_supervisor=supervisor)
        created_topics_data = ThesisTopicSerializer(created_topics, many=True).data

        # 2. Команды, где он назначен supervisor
        supervised_teams = Team.objects.filter(supervisor=supervisor)
        supervised_teams_data = TeamSerializer(supervised_teams, many=True).data

        return Response({
            "created_topics": created_topics_data,
            "supervised_teams": supervised_teams_data,
            "count": created_topics.count() + supervised_teams.count()
        })

class MyJoinRequestView(APIView):
    """Проверяет, есть ли активная заявка у текущего студента"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, "student_profile"):
            return Response({"error": "Only students can check join requests."}, status=403)

        student_profile = user.student_profile
        join_request = JoinRequest.objects.filter(student=student_profile, status="pending").first()

        if join_request:
            return Response({
                "team_id": join_request.team.id,
                "team_title": join_request.team.thesis_topic.title,
                "status": join_request.status
            }, status=200)

        return Response({"status": "no_request"}, status=200)

class MyJoinRequestsView(APIView):
    """ Get all join requests of the current student """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "student_profile"):
            return Response({"error": "Only students can view this."}, status=403)

        requests = JoinRequest.objects.filter(student=request.user.student_profile)
        serializer = JoinRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        """ Cancel join request """
        if not hasattr(request.user, "student_profile"):
            return Response({"error": "Only students can cancel."}, status=403)

        try:
            req = JoinRequest.objects.get(pk=pk, student=request.user.student_profile)
            if req.status != "pending":
                return Response({"error": "Only pending requests can be canceled."}, status=400)
            req.delete()
            return Response({"message": "Request canceled."})
        except JoinRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=404)

class JoinTeamView(APIView):
    """ Позволяет студенту подать заявку и присоединиться к команде """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        # Убедиться, что это студент
        if not hasattr(user, "student_profile"):
            return Response({"error": "Only students can join teams."}, status=status.HTTP_403_FORBIDDEN)

        student_profile = user.student_profile

        # ✅ 1. Проверка: уже состоит в команде
        if Team.objects.filter(members=student_profile).exists():
            return Response({"error": "You are already in a team."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 2. Проверка: есть ли уже PENDING заявка в ЛЮБУЮ команду
        if JoinRequest.objects.filter(student=student_profile, status="pending").exists():
            return Response({"error": "You have already applied to a team."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 3. Проверка: уже ли есть PENDING заявка именно в ЭТУ команду (опционально, но полезно)
        team = get_object_or_404(Team, pk=pk)

        if JoinRequest.objects.filter(team=team, student=student_profile, status='pending').exists():
            return Response({"error": "You already sent a join request to this team."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 4. Создание заявки
        JoinRequest.objects.create(team=team, student=student_profile)

        # ✅ 5. Уведомление владельцу
        send_notification(team.owner, f"{student_profile.first_name} {student_profile.last_name} wants to join your team.")

        return Response({"message": "Join request sent."}, status=status.HTTP_200_OK)



class MyTeamJoinRequestsView(APIView):
    """ Owner sees join requests for his team """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            team = Team.objects.get(owner=request.user)
            requests = JoinRequest.objects.filter(team=team).order_by('-created_at')  # Сортировка сверху вниз
            serializer = JoinRequestSerializer(requests, many=True)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"error": "You don't own any team."}, status=404)


class MySupervisorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "student_profile"):
            return Response({"error": "Only students can view this."}, status=403)

        try:
            team = Team.objects.get(members=request.user.student_profile)
        except Team.DoesNotExist:
            return Response({"detail": "No team found."}, status=404)

        supervisor_request = SupervisorRequest.objects.filter(team=team).order_by("-created_at").first()
        if not supervisor_request:
            return Response({"detail": "No supervisor request found."}, status=404)

        serializer = SupervisorRequestSerializer(supervisor_request)
        return Response(serializer.data)


class AcceptJoinRequestView(APIView):
    """ Accept a student into the team """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, student_id):
        try:
            team = Team.objects.get(pk=pk)
            if team.owner != request.user:
                return Response({"error": "Only the owner can accept requests."}, status=403)

            join_request = JoinRequest.objects.get(team=team, student_id=student_id, status='pending')
            team.members.add(join_request.student)
            join_request.status = 'accepted'
            join_request.save()

            send_notification(join_request.student.user, f"Your request to join '{team.thesis_topic.title}' was accepted.")
            return Response({"message": "Student added to the team."}, status=200)

        except (Team.DoesNotExist, JoinRequest.DoesNotExist):
            return Response({"error": "Team or join request not found."}, status=404)

class RejectJoinRequestView(APIView):
    """ Reject a student request """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, student_id):
        try:
            team = Team.objects.get(pk=pk)
            if team.owner != request.user:
                return Response({"error": "Only the owner can reject requests."}, status=403)

            join_request = JoinRequest.objects.get(team=team, student_id=student_id, status='pending')
            join_request.status = 'rejected'
            join_request.save()

            send_notification(join_request.student.user, f"Your request to join '{team.thesis_topic.title}' was rejected.")
            return Response({"message": "Request rejected."}, status=200)

        except (Team.DoesNotExist, JoinRequest.DoesNotExist):
            return Response({"error": "Team or join request not found."}, status=404)

# teams/views.py

class CreateSupervisorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, supervisor_id):
        user = request.user

        if not hasattr(user, "student_profile"):
            return Response({"error": "Only students can send supervisor requests."}, status=403)

        try:
            team = Team.objects.get(owner=user)
        except Team.DoesNotExist:
            return Response({"error": "Only team owners can send requests."}, status=403)

        # Проверка: уже есть активная заявка?
        if SupervisorRequest.objects.filter(team=team, status='pending').exists():
            return Response({"error": "You already have a pending request."}, status=400)

        if team.supervisor:
            return Response({"error": "Team already has supervisor."}, status=400)

        supervisor = get_object_or_404(SupervisorProfile, pk=supervisor_id)

        SupervisorRequest.objects.create(team=team, supervisor=supervisor)

        # Уведомление
        send_notification(supervisor.user, f"{user.student_profile.first_name} requests you as supervisor.")

        return Response({"message": "Request sent."})

class IncomingSupervisorRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "supervisor_profile"):
            return Response({"error": "Only supervisors can see requests."}, status=403)

        requests = SupervisorRequest.objects.filter(supervisor=request.user.supervisor_profile, status='pending')
        serializer = SupervisorRequestSerializer(requests, many=True)
        return Response(serializer.data)

class AcceptSupervisorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not hasattr(request.user, "supervisor_profile"):
            return Response({"error": "Only supervisors can accept."}, status=403)

        try:
            req = SupervisorRequest.objects.get(pk=request_id, supervisor=request.user.supervisor_profile)
        except SupervisorRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=404)

        team = req.team
        team.supervisor = request.user.supervisor_profile
        team.owner = request.user
        team.status = 'accepted'
        team.save()

        req.status = 'accepted'
        req.save()

        send_notification(team.owner, "Your supervisor request was accepted!")
        return Response({"message": "Team approved and assigned."})


class RejectSupervisorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not hasattr(request.user, "supervisor_profile"):
            return Response({"error": "Only supervisors can reject."}, status=403)

        try:
            req = SupervisorRequest.objects.get(pk=request_id, supervisor=request.user.supervisor_profile)
        except SupervisorRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=404)

        req.status = 'rejected'
        req.save()

        send_notification(req.team.owner, "Your supervisor request was rejected.")
        return Response({"message": "Request rejected."})

class CancelSupervisorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            team = Team.objects.get(owner=request.user)
            req = SupervisorRequest.objects.get(team=team, status='pending')
            req.delete()
            return Response({"message": "Request canceled."})
        except (Team.DoesNotExist, SupervisorRequest.DoesNotExist):
            return Response({"error": "No pending request."}, status=404)
