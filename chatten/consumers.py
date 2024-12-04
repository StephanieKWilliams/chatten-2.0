# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from notifications.signals import notify
from chat.models import ChatSessionMember
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_session_id = self.scope['url_route']['kwargs']['chat_session_id']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{self.chat_session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive notification from back-end (Celery task via notify.send)
    async def chat_notification(self, event):
        message = event['message']
        
        # Send the message to WebSocket client
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # This method will listen to the notification signal
    def notify_message_handler(self, sender, recipient, **kwargs):
        message = kwargs.get('message')
        
        # Send message over WebSocket to the client
        self.send({
            'type': 'chat_notification',
            'message': message
        })
