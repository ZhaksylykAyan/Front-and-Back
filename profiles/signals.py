from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, SupervisorProfile, DeanOfficeProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Automatically create a profile for the user based on their role """
    if created:
        if instance.role == "Student":
            StudentProfile.objects.create(user=instance)
        elif instance.role == "Supervisor":
            SupervisorProfile.objects.create(user=instance)
        elif instance.role == "Dean Office":
            DeanOfficeProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Save the user profile when user is saved """
    if hasattr(instance, "student_profile"):
        instance.student_profile.save()
    elif hasattr(instance, "supervisor_profile"):
        instance.supervisor_profile.save()
    elif hasattr(instance, "dean_office_profile"):
        instance.dean_office_profile.save()
