from django.urls import path
from .views import ProfileCompletionView, SkillListView

urlpatterns = [
    path('complete-profile/', ProfileCompletionView.as_view(), name='complete-profile'),
    path('skills/', SkillListView.as_view(), name='skills-list'),
]