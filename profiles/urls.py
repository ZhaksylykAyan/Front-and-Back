from django.urls import path
from .views import ProfileCompletionView, SkillListView, StudentProfileDetailView, SupervisorListView, \
    SupervisorProfileDetailView

urlpatterns = [
    path('complete-profile/', ProfileCompletionView.as_view(), name='complete-profile'),
    path('skills/', SkillListView.as_view(), name='skills-list'),
    path('students/<int:pk>/', StudentProfileDetailView.as_view(), name='student-detail'),
    path('supervisors/', SupervisorListView.as_view(), name='supervisor-list'),
    path('supervisors/<int:pk>/', SupervisorProfileDetailView.as_view(), name='supervisor-detail'),
]