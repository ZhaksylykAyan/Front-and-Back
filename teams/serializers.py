from rest_framework import serializers

from topics.serializers import ThesisTopicSerializer
from .models import Team, JoinRequest, SupervisorRequest, Like
from profiles.models import SupervisorProfile
from profiles.serializers import StudentProfileSerializer, SupervisorShortSerializer
from profiles.serializers import SupervisorProfileSerializer

class TeamSerializer(serializers.ModelSerializer):
    members = StudentProfileSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), required=False)
    thesis_topic = ThesisTopicSerializer()
    supervisor = SupervisorShortSerializer(read_only=True)
    thesis_name = serializers.CharField(source='thesis_topic.title', read_only=True)
    thesis_description = serializers.CharField(source='thesis_topic.description', read_only=True)
    required_skills = serializers.SerializerMethodField(read_only=True)
    thesis_id = serializers.IntegerField(source='thesis_topic.id', read_only=True)

    class Meta:
        model = Team
        fields = ['id','thesis_id', 'thesis_topic', 'thesis_name', 'thesis_description', 'owner', 'members', 'status', 'supervisor', 'required_skills']

    def get_required_skills(self, obj):
        return [skill.name for skill in obj.thesis_topic.required_skills.all()]

    def validate(self, data):
        user = self.context['request'].user
        if hasattr(user, 'student_profile'):
            if user.student_profile.teams.filter(status="open").exists():
                raise serializers.ValidationError("You can only apply to 1 team at a time.")
        return data

class JoinRequestSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    team_members = serializers.SerializerMethodField()

    class Meta:
        model = JoinRequest
        fields = ['id', 'team', 'student', 'status', 'created_at', 'team_members']

    def get_team_members(self, obj):
        members = obj.team.members.all()
        return StudentProfileSerializer(members, many=True).data

class SupervisorRequestSerializer(serializers.ModelSerializer):
    supervisor = SupervisorProfileSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = SupervisorRequest
        fields = ['id', 'team', 'supervisor', 'status', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'team', 'user', 'created_at']
        read_only_fields = ['user']