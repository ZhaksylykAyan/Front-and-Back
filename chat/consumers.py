from channels.generic.websocket import AsyncWebsocketConsumer
import json
from chat.models import Chat, Message, UserStatus
from django.utils import timezone
from django.contrib.auth import get_user_model
import asyncio

User = get_user_model()

async def run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_group_name = f"chat_{self.chat_id}"

        if self.user.is_authenticated:
            await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
            await self.accept()

            await self.set_user_online()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.set_user_offline()
            await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")
        message = data.get("message")

        if event_type == "ping":
            await self.set_user_online()
            return

        if event_type == "typing":
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "user_typing",
                    "user": self.user.email,
                }
            )
            return

        if message:
            msg = await self.create_message(message)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.email,
                    "timestamp": msg.timestamp.isoformat(),
                    "chat_id": self.chat_id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "chat_id": event["chat_id"],
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user": event["user"]
        }))

    async def set_user_online(self):
        def update_status():
            status, _ = UserStatus.objects.get_or_create(user=self.user)
            status.is_online = True
            status.last_seen = timezone.now()
            status.save()
        await run_sync(update_status)

    async def set_user_offline(self):
        def mark_offline():
            try:
                status = UserStatus.objects.get(user=self.user)
                status.is_online = False
                status.last_seen = timezone.now()
                status.save()
            except UserStatus.DoesNotExist:
                pass
        await run_sync(mark_offline)

    async def create_message(self, content):
        def save_message():
            chat = Chat.objects.get(id=self.chat_id)
            msg = Message(chat=chat, sender=self.user, content=content)
            msg.save()
            return msg
        return await run_sync(save_message)
