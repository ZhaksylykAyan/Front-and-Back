from django.urls import path
from .views import TeamCreateView, TeamListView, TeamDetailView, \
    MyTeamView, JoinTeamView, AcceptJoinRequestView, RejectJoinRequestView, MyJoinRequestView, \
    MyJoinRequestsView, MyTeamJoinRequestsView, CreateSupervisorRequestView, IncomingSupervisorRequestsView, \
    AcceptSupervisorRequestView, RejectSupervisorRequestView, CancelSupervisorRequestView, SupervisorProjectsView, \
    MySupervisorRequestView, LikedProjectsView, LikeToggleView

urlpatterns = [
    path('create/', TeamCreateView.as_view(), name='create-team'),
    path('', TeamListView.as_view(), name='list-teams'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('my-team-join-requests/', MyTeamJoinRequestsView.as_view(), name='my-team-join-requests'),
    path('<int:pk>/join-requests/<int:student_id>/accept/', AcceptJoinRequestView.as_view(),
         name='accept-join-request'),
    path('<int:pk>/join-requests/<int:student_id>/reject/', RejectJoinRequestView.as_view(),
         name='reject-join-request'),
    path('<int:pk>/join/', JoinTeamView.as_view(), name='join-team'),
    path('my-join-requests/', MyJoinRequestsView.as_view(), name='my-join-requests'),
    path('my-join-requests/<int:pk>/', MyJoinRequestsView.as_view(), name='cancel-join-request'),
    path('my/', MyTeamView.as_view(), name='my-team'),
    path('my-projects/', SupervisorProjectsView.as_view(), name='supervisor-projects'),
    path('my-join-request/', MyJoinRequestView.as_view(), name='my-join-request'),
    path('my-supervisor-request/', MySupervisorRequestView.as_view()),
    path('supervisor-request/<int:supervisor_id>/', CreateSupervisorRequestView.as_view(),
         name='supervisor-request-create'),
    path('supervisor-requests/incoming/', IncomingSupervisorRequestsView.as_view()),
    path('supervisor-requests/<int:request_id>/accept/', AcceptSupervisorRequestView.as_view()),
    path('supervisor-requests/<int:request_id>/reject/', RejectSupervisorRequestView.as_view()),
    path('supervisor-requests/cancel/', CancelSupervisorRequestView.as_view()),
    path('likes/', LikedProjectsView.as_view(), name='liked-projects'),
    path('likes/toggle/<int:team_id>/', LikeToggleView.as_view(), name='like-toggle'),
]
