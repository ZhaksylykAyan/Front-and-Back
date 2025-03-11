from django.urls import path
from .views import ThesisTopicCreateView, ThesisTopicListView, ThesisTopicDetailView

urlpatterns = [
    path('create/', ThesisTopicCreateView.as_view(), name='create-topic'),
    path('', ThesisTopicListView.as_view(), name='list-topics'),
    path('<int:pk>/', ThesisTopicDetailView.as_view(), name='topic-detail'),
]