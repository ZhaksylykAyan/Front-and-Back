from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from chat.models import Chat, Message, UserStatus
from users.models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from chat.serializers import ChatSerializer, MessageSerializer, UserStatusSerializer
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone

class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'chat_id'

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, participants=self.request.user)
        return Message.objects.filter(chat=chat)

    def perform_create(self, serializer):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'], participants=self.request.user)
        serializer.save(sender=self.request.user, chat=chat)


class MarkMessageReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        msg = get_object_or_404(Message, id=id, chat__participants=request.user)
        msg.is_read = True
        msg.save()
        return Response({"status": "marked as read"})


class UserStatusView(APIView):
    def get(self, request, user_id):
        status = get_object_or_404(UserStatus, user__id=user_id)
        serializer = UserStatusSerializer(status)
        data = serializer.data

        now = timezone.now()
        last_seen = status.last_seen

        # Если прошло больше 60 секунд с момента последнего пинга
        if now - last_seen > timedelta(seconds=60):
            data["is_online"] = False
        else:
            data["is_online"] = True

        return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_or_get_chat(request):
    target_user_id = request.data.get("user_id")
    if not target_user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = CustomUser.objects.get(id=target_user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    current_user = request.user

    # Поиск существующего чата с этими двумя участниками
    existing_chats = Chat.objects.filter(participants=current_user).filter(participants=target_user)
    for chat in existing_chats:
        if chat.participants.count() == 2:
            serializer = ChatSerializer(chat)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # Чата нет — создаём новый
    new_chat = Chat.objects.create()
    new_chat.participants.set([current_user, target_user])
    new_chat.save()

    serializer = ChatSerializer(new_chat)
    return Response(serializer.data, status=status.HTTP_201_CREATED)