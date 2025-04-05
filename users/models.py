from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from profiles.models import StudentProfile, SupervisorProfile, DeanOfficeProfile
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Supervisor', 'Supervisor'),
        ('Dean Office', 'Dean Office'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    is_profile_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    block_duration = models.IntegerField(default=5)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.role == "Student" and not hasattr(self, "student_profile"):
            StudentProfile.objects.get_or_create(user=self)
        elif self.role == "Supervisor" and not hasattr(self, "supervisor_profile"):
            SupervisorProfile.objects.get_or_create(user=self)
        elif self.role == "Dean Office" and not hasattr(self, "dean_office_profile"):
            DeanOfficeProfile.objects.get_or_create(user=self)

    def __str__(self):
        return f"{self.email} ({self.role})"

class AccessLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} — {self.action.upper()} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
