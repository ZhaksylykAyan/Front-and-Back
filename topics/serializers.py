from rest_framework import serializers
from topics.models import ThesisTopic
from teams.models import Team


class ThesisTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesisTopic
        fields = '__all__'

    def validate(self, data):
        """ Ensure only valid users can create thesis topics """
        user = self.context['request'].user

        # Students can create only 1 topic, but if they are already in a team, they cannot create one
        if hasattr(user, 'student_profile'):
            if user.student_profile.teams.exists():
                raise serializers.ValidationError("You cannot create a thesis topic while you are already in a team.")
            if ThesisTopic.objects.filter(created_by_student=user.student_profile).exists():
                raise serializers.ValidationError("Students can create only one thesis topic.")

        # Supervisors can create up to 10 thesis topics, but their total teams + topics should be <= 10
        elif hasattr(user, 'supervisor_profile'):
            total_owned = Team.objects.filter(owner=user).count() + ThesisTopic.objects.filter(
                created_by_supervisor=user.supervisor_profile).count()
            if total_owned >= 10:
                raise serializers.ValidationError(
                    "You cannot create a new thesis topic because you already have 10 topics/teams combined.")

        else:
            raise serializers.ValidationError("Only students and supervisors can create a thesis topic.")

        return data

    def create(self, validated_data):
        """ Auto-create a team when a thesis topic is created """
        user = self.context['request'].user
        if hasattr(user, 'student_profile'):
            validated_data['created_by_student'] = user.student_profile
        elif hasattr(user, 'supervisor_profile'):
            validated_data['created_by_supervisor'] = user.supervisor_profile
        thesis_topic = super().create(validated_data)

        # Auto-create a team with the creator as the owner
        Team.objects.create(
            thesis_topic=thesis_topic,
            owner=user,
            status="open"
        )

        return thesis_topic