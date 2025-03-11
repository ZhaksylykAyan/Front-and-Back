from django.urls import path
from .views import (
    RegisterView, CustomTokenObtainPairView, UserDetailView,
    PasswordResetRequestView, PasswordResetConfirmView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Forgot Password URLs
    path("forgot-password/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("reset-password/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
