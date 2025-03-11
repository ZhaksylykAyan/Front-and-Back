from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Skill, StudentProfile, SupervisorProfile, DeanOfficeProfile


class SkillSerializer(serializers.ModelSerializer):
    """ Serializer for the Skill model """
    class Meta:
        model = Skill
        fields = ['id', 'name']


class StudentProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Student Profile """
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True, source='skills')
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def validate_skill_ids(self, value):
        """ Ensure students do not select more than 5 skills """
        if len(value) > 5:
            raise serializers.ValidationError("Students can select a maximum of 5 skills.")
        return value

    def update(self, instance, validated_data):
        """ Ensure the profile is updated correctly """
        skills = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        if skills is not None:
            instance.skills.set(skills)  # Update skills properly
        instance.update_profile_completion()
        return instance


class SupervisorProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Supervisor Profile """
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True, source='skills')
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)

    class Meta:
        model = SupervisorProfile
        fields = '__all__'

    def validate_skill_ids(self, value):
        """ Ensure supervisors do not select more than 10 skills """
        if len(value) > 10:
            raise serializers.ValidationError("Supervisors can select a maximum of 10 skills.")
        return value

    def update(self, instance, validated_data):
        """ Ensure the profile is updated correctly """
        skills = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        if skills is not None:
            instance.skills.set(skills)  # Update skills properly
        instance.update_profile_completion()
        return instance


class DeanOfficeProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Dean Office Profile """
    is_profile_completed = serializers.BooleanField(source="user.is_profile_completed", read_only=True)

    class Meta:
        model = DeanOfficeProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        """ Ensure the profile is updated correctly """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.update_profile_completion()
        return instance
