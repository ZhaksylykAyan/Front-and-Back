from datetime import timedelta
from django.core.cache import cache
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from users.models import CustomUser
from profiles.models import StudentProfile, SupervisorProfile, DeanOfficeProfile
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['is_profile_completed'] = user.is_profile_completed
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")
        now = timezone.now()

        # IP логика
        ip_address = request.META.get("REMOTE_ADDR", "unknown")
        cache_key = f"login_attempts:{ip_address}"
        cache_block_key = f"login_blocked:{ip_address}"

        # 1. Проверка блокировки по IP
        if cache.get(cache_block_key):
            raise AuthenticationFailed("Too many login attempts from this IP. Try again later.")

        # 2. Проверка email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Увеличиваем попытки по IP даже при неверном email
            cache.incr(cache_key)
            cache.expire(cache_key, 600)  # 10 мин
            raise AuthenticationFailed("Invalid credentials")

        # 3. Проверка блокировки пользователя
        if user.blocked_until and now < user.blocked_until:
            remaining = (user.blocked_until - now).seconds // 60
            raise AuthenticationFailed(f"Account is temporarily blocked. Try again in {remaining} minute(s).")

        # 4. Сброс старых попыток (если больше 10 мин прошло)
        if user.last_failed_login and now - user.last_failed_login > timedelta(minutes=10):
            user.failed_login_attempts = 0
            user.block_duration = 5
            user.save()

        # 5. Проверка пароля
        if not user.check_password(password):
            # Защита от частых запросов (<1 секунда)
            if user.last_failed_login and (now - user.last_failed_login).total_seconds() < 1:
                raise AuthenticationFailed("Too many login attempts. Please wait a moment.")

            # IP-блокировка
            ip_attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, ip_attempts, timeout=600)  # сброс через 10 минут

            if ip_attempts >= 5:
                cache.set(cache_block_key, True, timeout=900)  # блок IP на 15 минут
                raise AuthenticationFailed("Too many login attempts from your IP. Try again in 15 minutes.")

            # Логика блокировки пользователя
            user.failed_login_attempts += 1
            user.last_failed_login = now

            if user.failed_login_attempts >= 3:
                block_minutes = user.block_duration
                user.blocked_until = now + timedelta(minutes=block_minutes)
                user.block_duration = min(user.block_duration + 5, 30)
                user.failed_login_attempts = 0
                user.last_failed_login = None
                user.save()
                raise AuthenticationFailed({
                    "detail": "Account is temporarily blocked. Try again in a few minutes.",
                    "blocked": True,
                    "blocked_until": user.blocked_until,
                })

            user.save()
            attempts_left = 3 - user.failed_login_attempts
            raise AuthenticationFailed(f"Incorrect password. Attempts left: {attempts_left}")

        # 6. Успешный вход — всё сбрасываем
        cache.delete(cache_key)
        cache.delete(cache_block_key)

        user.failed_login_attempts = 0
        user.blocked_until = None
        user.block_duration = 5
        user.last_failed_login = None
        user.save()

        return super().validate(attrs)


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
