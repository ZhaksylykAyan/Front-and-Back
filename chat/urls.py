from django.urls import path
from chat.views import (
    ChatListView, ChatDetailView, MessageListCreateView,
    MarkMessageReadView, UserStatusView, start_or_get_chat
)

urlpatterns = [
    path("chats/", ChatListView.as_view()),
    path("chats/<int:chat_id>/", ChatDetailView.as_view()),
    path("chats/<int:chat_id>/messages/", MessageListCreateView.as_view()),
    path("messages/<int:id>/read/", MarkMessageReadView.as_view()),
    path("users/<int:user_id>/status/", UserStatusView.as_view()),
    path("chats/start/", start_or_get_chat),
]
