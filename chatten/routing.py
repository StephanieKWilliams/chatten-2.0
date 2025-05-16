# routing.py
from django.urls import path ,re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
  
     # path("ws/chats/<chat_session_id>/", ChatConsumer.as_asgi()), 
     re_path(r'ws/chats/(?P<chat_session_uri>\w+)/$', ChatConsumer.as_asgi()),
]
