import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """ WebSocket Consumer to handle real-time notifications """

    async def connect(self):
        """ Connect the user to the WebSocket """
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """ Disconnect the user """
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """ Handle incoming messages (not needed for notifications) """
        pass

    async def send_notification(self, event):
        """ Send a real-time notification to the user """
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))