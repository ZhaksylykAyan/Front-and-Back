from django.urls import path
from .views import TeamCreateView, TeamListView, TeamDetailView, ApplyToSupervisorView, ApproveTeamView, RejectTeamView

urlpatterns = [
    path('create/', TeamCreateView.as_view(), name='create-team'),
    path('', TeamListView.as_view(), name='list-teams'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('<int:pk>/apply/', ApplyToSupervisorView.as_view(), name='apply-to-supervisor'),
    path('<int:pk>/approve/', ApproveTeamView.as_view(), name='approve-team'),
    path('<int:pk>/reject/', RejectTeamView.as_view(), name='reject-team'),
]