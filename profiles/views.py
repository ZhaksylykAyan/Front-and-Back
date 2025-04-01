from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from teams.models import Team
from teams.serializers import TeamSerializer
from .models import StudentProfile, SupervisorProfile, DeanOfficeProfile, Skill
from .serializers import (
    StudentProfileSerializer,
    SupervisorProfileSerializer,
    DeanOfficeProfileSerializer,
    SkillSerializer
)

User = get_user_model()


class SkillListView(generics.ListAPIView):
    """ API to get the list of available skills """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]


class ProfileCompletionView(generics.RetrieveUpdateAPIView):
    """
    API to retrieve and update user profile (Student, Supervisor, Dean Office)
    - Users can only access their own profile
    - Ensures profile completion
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """ Returns the correct serializer based on user role """
        user = self.request.user
        if user.role == "Student":
            return StudentProfileSerializer
        elif user.role == "Supervisor":
            return SupervisorProfileSerializer
        elif user.role == "Dean Office":
            return DeanOfficeProfileSerializer
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        """ Return the appropriate profile based on user role """
        user = self.request.user
        if user.role == "Student":
            return user.student_profile
        elif user.role == "Supervisor":
            return user.supervisor_profile
        elif user.role == "Dean Office":
            return user.dean_office_profile
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """ Update the user profile and check if completed """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # This will trigger the profile completion check

        return Response({"message": "Profile updated successfully", "is_profile_completed": instance.user.is_profile_completed})

class StudentProfileDetailView(generics.RetrieveAPIView):
    queryset = StudentProfile.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            profile = StudentProfile.objects.get(pk=pk)
        except StudentProfile.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        serializer = StudentProfileSerializer(profile)
        data = serializer.data

        # ✅ Импортируем TeamSerializer внутри метода, чтобы избежать цикличности
        team = profile.teams.first()
        if team:
            from teams.serializers import TeamSerializer
            team_serializer = TeamSerializer(team, context={"request": request})
            data['team'] = team_serializer.data
        else:
            data['team'] = None

        return Response(data)

class SupervisorListView(generics.ListAPIView):
    """
    API to list all supervisors with their profiles and skills
    """
    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorProfileSerializer
    permission_classes = [IsAuthenticated]

class SupervisorProfileDetailView(generics.RetrieveAPIView):
    """
    Публичный просмотр профиля супервизора по его user.id (primary_key)
    """
    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorProfileSerializer
    permission_classes = [permissions.AllowAny]  # Публичный доступ

