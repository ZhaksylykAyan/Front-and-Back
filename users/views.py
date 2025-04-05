import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import AccessLog
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from .serializers import (
    UserRegistrationSerializer, CustomTokenObtainPairSerializer,
    UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()
logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        ip = get_client_ip(request)

        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                user = User.objects.get(email=email)

                # IP-логика
                if user.last_login_ip != ip:
                    logger.warning(f"🕵️ New login IP detected: {ip} for {email}")
                user.last_login_ip = ip

                # Сброс безопасный, но не обязателен — уже делается в validate()
                user.save()

                logger.info(f"✅ JWT Login: {email} (IP: {ip})")
                AccessLog.objects.create(
                    user=user,
                    action="login",
                    ip_address=ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

            return response

        except AuthenticationFailed as e:
            logger.warning(f"❌ Failed login: {email} (IP: {ip}) — {str(e)}")
            raise


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            logger.info(f"Обновление токена (IP: {get_client_ip(request)})")

        return response


class ManualLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        ip = get_client_ip(request)
        logger.info(f"JWT-выход: {user.email} (IP: {ip})")
        AccessLog.objects.create(
            user=user,
            action='logout',
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return Response({"message": "Logout logged"})


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                user = serializer.save()
                logger.info(f"Успешная регистрация: {user.email}")
                return Response({"message": "User registered successfully.", "role": user.role},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Ошибка регистрации пользователя: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            logger.warning(f"Запрос сброса пароля: email не найден — {email}")
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        try:
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Отправлен email сброса пароля пользователю: {user.email}")
            return Response({"message": "If your email is registered, you will receive a password reset link."})
        except Exception as e:
            logger.error("Ошибка при отправке письма для сброса пароля: %s", e)
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def put(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                logger.warning("Невалидный токен сброса пароля для UID: %s", uid)
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            logger.info(f"Пароль сброшен пользователем: {user.email} (IP: {get_client_ip(request)})")
            return Response({"message": "Password has been reset successfully."})
        except Exception as e:
            logger.error("Ошибка подтверждения сброса пароля: %s", e)
            return Response({"error": "Invalid token or user not found"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileCompletionCheckView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"is_profile_completed": request.user.is_profile_completed})
