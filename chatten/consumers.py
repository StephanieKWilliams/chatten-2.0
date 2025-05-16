import json
from channels.generic.websocket import AsyncWebsocketConsumer
from notifications.signals import notify
from channels.layers import get_channel_layer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the chat session ID and user from the WebSocket scope
        self.chat_session_id = self.scope['url_route']['kwargs']['chat_session_id']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{self.chat_session_id}'
        print(f"Scope: {self.scope}")  # Add this line to inspect the scope
        print(f"User: {self.user}")  
        # Print to track connection initiation
        print(f"Attempting to connect to chat session: {self.chat_session_id}")
        print(f"User: {self.user.username}")
        
        # Subscribe to notification signals
        notify.connect(self.notify_message_handler)

        # Join the WebSocket room group
        print(f"Attempting to join group: {self.room_group_name}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connection established for: {self.room_group_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Unsubscribe from notification signals when disconnected
        notify.disconnect(self.notify_message_handler)
        
        print(f"WebSocket connection closed for: {self.room_group_name}")

    async def receive(self, text_data):
        # You can print received data here if necessary
        print(f"Received message from WebSocket: {text_data}")

    async def chat_notification(self, event):
        # Handle incoming notification event
        try:
            print(f"Received notification event: {event}")

            # Send the message to WebSocket client
            await self.send(text_data=json.dumps({
                'message': event['message']  # Sending the actual notification message
            }))
        except Exception as e:
            print(f"Error handling notification: {str(e)}")

    async def notify_message_handler(self, sender, recipient, **kwargs):
        # Handle the notification message and send it to the group
        message = kwargs.get('message')
        
        if message:
            print(f"Notification message received: {message}")  # Debug print
        else:
            print("No message received in notify handler.")  # Debug print

        # Send notification message to the WebSocket group
        channel_layer = get_channel_layer()
        if channel_layer:
            print(f"Sending notification to group: {self.room_group_name}")
            await channel_layer.group_send(
                self.room_group_name,  # Send message to the specific group
                {
                    'type': 'chat_notification',  # Custom event type for WebSocket consumer
                    'message': message,  # Message to send
                }
            )
        else:
            print("Channel layer not found.")  # If no channel layer is available
