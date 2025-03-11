from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Skill(models.Model):
    """ Model to store skills """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    """ Profile model for students """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        primary_key=True
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    gpa = models.FloatField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def clean(self):
        """ Ensure students do not select more than 5 skills """
        if self.pk and self.skills.count() > 5:
            raise ValidationError("Students can select a maximum of 5 skills.")

    def update_profile_completion(self):
        """ Check if profile is completed and update the user field """
        required_fields = [self.first_name, self.last_name, self.specialization, self.gpa]
        self.user.is_profile_completed = all(required_fields) and self.skills.exists()
        self.user.save()

    def save(self, *args, **kwargs):
        if not self.pk and StudentProfile.objects.filter(user=self.user).exists():
            raise ValidationError("A profile for this user already exists.")
        super().save(*args, **kwargs)
        self.update_profile_completion()

    def __str__(self):
        return f"{self.user.email} (Student)"


class SupervisorProfile(models.Model):
    """ Profile model for supervisors """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervisor_profile",
        primary_key=True
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def clean(self):
        """ Ensure supervisors do not select more than 10 skills """
        if self.pk and self.skills.count() > 10:
            raise ValidationError("Supervisors can select a maximum of 10 skills.")

    def update_profile_completion(self):
        """ Check if profile is completed and update the user field """
        required_fields = [self.first_name, self.last_name, self.degree]
        self.user.is_profile_completed = all(required_fields) and self.skills.exists()
        self.user.save()

    def save(self, *args, **kwargs):
        if not self.pk and SupervisorProfile.objects.filter(user=self.user).exists():
            raise ValidationError("A profile for this user already exists.")
        super().save(*args, **kwargs)
        self.update_profile_completion()

    def __str__(self):
        return f"{self.user.email} (Supervisor)"


class DeanOfficeProfile(models.Model):
    """ Profile model for Dean's Office """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dean_office_profile",
        primary_key=True
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    job_role = models.CharField(max_length=50, choices=[("manager", "Manager"), ("dean", "Dean")], blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def update_profile_completion(self):
        """ Check if profile is completed and update the user field """
        required_fields = [self.first_name, self.last_name, self.job_role]
        self.user.is_profile_completed = all(required_fields)
        self.user.save()

    def save(self, *args, **kwargs):
        if not self.pk and DeanOfficeProfile.objects.filter(user=self.user).exists():
            raise ValidationError("A profile for this user already exists.")
        super().save(*args, **kwargs)
        self.update_profile_completion()

    def __str__(self):
        return f"{self.user.email} (Dean Office)"


# 🚀 Signal to auto-create profiles after user creation
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """ Automatically create a profile for new users based on role """
    if created:
        if instance.role == "Student" and not hasattr(instance, "student_profile"):
            StudentProfile.objects.create(user=instance)
        elif instance.role == "Supervisor" and not hasattr(instance, "supervisor_profile"):
            SupervisorProfile.objects.create(user=instance)
        elif instance.role == "Dean Office" and not hasattr(instance, "dean_office_profile"):
            DeanOfficeProfile.objects.create(user=instance)
