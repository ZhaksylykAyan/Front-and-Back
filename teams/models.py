from django.db import models
from django.conf import settings
from profiles.models import StudentProfile, SupervisorProfile, Skill
from topics.models import ThesisTopic

class Team(models.Model):
    """ Model for thesis teams """
    id = models.AutoField(primary_key=True)
    thesis_topic = models.OneToOneField(ThesisTopic, on_delete=models.CASCADE, related_name="team")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_teams")
    members = models.ManyToManyField(StudentProfile, related_name="teams", blank=True)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending Approval"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )

    def has_required_skills(self):
        """ Checks if the team collectively meets at least 4 required skills """
        team_skills = set(skill.name for student in self.members.all() for skill in student.skills.all())
        required_skills = set(skill.name for skill in self.thesis_topic.required_skills.all())
        return len(team_skills.intersection(required_skills)) >= 4

    def apply_to_supervisor(self):
        """ Allow team to apply to the supervisor for approval """
        if not self.has_required_skills():
            raise ValueError("Team does not meet the minimum required skills.")
        self.status = "pending"
        self.save()

    def approve_team(self, supervisor):
        """ Supervisor approves the team and becomes the new owner """
        if self.status != "pending":
            raise ValueError("Only pending teams can be approved.")
        if supervisor.teams.count() >= 10:
            raise ValueError("Supervisor cannot own more than 10 teams.")
        self.supervisor = supervisor
        self.owner = supervisor.user
        self.status = "approved"
        self.save()

    def reject_team(self):
        """ Supervisor rejects the team """
        self.status = "rejected"
        self.save()

    def __str__(self):
        return f"Team for {self.thesis_topic.title} (Status: {self.status})"