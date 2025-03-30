from rest_framework import serializers

from profiles.models import Skill
from profiles.serializers_shared import SkillSerializer
from teams.models import Team, JoinRequest
from .models import ThesisTopic

class ThesisTopicSerializer(serializers.ModelSerializer):
    required_skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True)

    class Meta:
        model = ThesisTopic
        fields = '__all__'

    def validate(self, data):
        if self.instance:
            return data
        user = self.context['request'].user

        # ==== STUDENT ====
        if hasattr(user, 'student_profile'):
            #Студент уже создал проект
            if ThesisTopic.objects.filter(created_by_student=user.student_profile).exists():
                raise serializers.ValidationError("Students can create only one thesis topic.")

            #Студент уже в команде
            if Team.objects.filter(members=user.student_profile).exists():
                raise serializers.ValidationError("You are already part of a team and cannot create a new one.")

            #Студент уже подал заявку
            if JoinRequest.objects.filter(student=user.student_profile, status='pending').exists():
                raise serializers.ValidationError("You have a pending join request and cannot create a new team.")

        # ==== SUPERVISOR ====
        elif hasattr(user, 'supervisor_profile'):
            created_topics_count = ThesisTopic.objects.filter(created_by_supervisor=user.supervisor_profile).count()
            supervised_teams_count = Team.objects.filter(supervisor=user.supervisor_profile).count()

            total = created_topics_count + supervised_teams_count
            if total >= 10:
                raise serializers.ValidationError("Supervisor limit exceeded. Max 10 projects/teams allowed.")

        else:
            raise serializers.ValidationError("Only students and supervisors can create projects.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        if hasattr(user, 'student_profile'):
            validated_data['created_by_student'] = user.student_profile
        elif hasattr(user, 'supervisor_profile'):
            validated_data['created_by_supervisor'] = user.supervisor_profile

        thesis_topic = super().create(validated_data)

        # Auto-create team
        team = Team.objects.create(
            thesis_topic=thesis_topic,
            owner=user,
            status="open"
        )

        if hasattr(user, 'student_profile'):
            team.members.add(user.student_profile)

        if hasattr(user, 'supervisor_profile'):
            team.supervisor = user.supervisor_profile
            team.save()

        return thesis_topic