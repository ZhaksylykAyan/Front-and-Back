from django.db import models
from profiles.models import Skill, StudentProfile, SupervisorProfile

class ThesisTopic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    title_kz = models.CharField(max_length=255, blank=True, null=True)
    title_ru = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, related_name="thesis_topics")
    created_by_student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, null=True, blank=True,
                                              related_name="thesis_topic")
    created_by_supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title