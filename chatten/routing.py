# routing.py
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<chat_session_id>/", ChatConsumer.as_asgi()),
]
