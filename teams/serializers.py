from rest_framework import serializers
from .models import Team
from profiles.models import StudentProfile, SupervisorProfile
from topics.models import ThesisTopic

class TeamSerializer(serializers.ModelSerializer):
    """ Serializer for Team model """
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=StudentProfile.objects.all())
    owner = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), required=False)
    thesis_topic = serializers.PrimaryKeyRelatedField(queryset=ThesisTopic.objects.all())

    class Meta:
        model = Team
        fields = ['id', 'thesis_topic', 'owner', 'members', 'status', 'supervisor']

    def validate(self, data):
        """ Ensure a supervisor does not exceed 10 teams including thesis topics they created """
        user = self.context['request'].user

        # Ensure students can only apply to one team at a time
        if hasattr(user, 'student_profile'):
            if user.student_profile.teams.filter(status="open").exists():
                raise serializers.ValidationError("You can only apply to 1 team at a time.")

        # Ensure supervisors do not exceed 10 total (teams + topics)
        elif hasattr(user, 'supervisor_profile'):
            total_owned = Team.objects.filter(owner=user).count() + ThesisTopic.objects.filter(created_by_supervisor=user.supervisor_profile).count()
            if total_owned >= 10:
                raise serializers.ValidationError("Supervisors cannot own more than 10 teams including thesis topics they created.")

        return data

    # def create(self, validated_data):
    #     """ Create a new team with the correct owner """
    #     user = self.context['request'].user
    #     if hasattr(user, 'student_profile'):
    #         validated_data['owner'] = user
    #     elif hasattr(user, 'supervisor_profile'):
    #         validated_data['owner'] = user
    #     return super().create(validated_data)