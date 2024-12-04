"""
ASGI config for chatten project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatten.settings')

# application = get_asgi_application()


# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import ChatConsumer  # Import your WebSocket consumer
from django.urls import path , include
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatten.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<chat_session_id>/", ChatConsumer.as_asgi()),  # WebSocket URL
        ])
    ),
})
