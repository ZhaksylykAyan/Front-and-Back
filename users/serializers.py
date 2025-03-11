from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction

from profiles.models import StudentProfile, SupervisorProfile, DeanOfficeProfile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['is_profile_completed'] = user.is_profile_completed
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('confirm_password')
            email = validated_data['email']
            password = validated_data['password']

            # Determine role from email BEFORE @ symbol
            email_prefix = email.split('@')[0]
            if '-' in email_prefix:
                role = 'Dean Office'
            elif '.' in email_prefix:
                role = 'Supervisor'
            elif '_' in email_prefix:
                role = 'Student'
            else:
                role = 'Student'

            user = User.objects.create_user(email=email, password=password, role=role)

            # Create profile
            if role == 'Student' and not StudentProfile.objects.filter(user=user).exists():
                StudentProfile.objects.create(user=user)
            elif role == 'Supervisor' and not SupervisorProfile.objects.filter(user=user).exists():
                SupervisorProfile.objects.create(user=user)
            elif role == 'Dean Office' and not DeanOfficeProfile.objects.filter(user=user).exists():
                DeanOfficeProfile.objects.create(user=user)

            return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'is_profile_completed')


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6, max_length=100)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data
