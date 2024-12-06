# tasks.py
from celery import shared_task
from notifications.signals import notify
from .models import ChatSession
from django.contrib.auth import get_user_model


@shared_task
def send_chat_notification(chat_session_id, user_id):
    # Fetch the chat session and user details
    User = get_user_model()
    chat_session = ChatSession.objects.get(id=chat_session_id)
    user = User.objects.get(id=user_id)

    # Prepare notification arguments
    notif_args = {
        'sender': user,  # The actor (sender)
        'source_display_name': user.get_full_name(),
        'category': 'chat',
        'action': 'Sent',
        'obj': chat_session.id,
        'verb': 'You have a new message',
        'silent': True,
        'extra_data': {'uri': chat_session.uri}
    }
    # Identify the recipients (all other users in the chat session)
    recipients = chat_session.members.exclude(user=user)

    # Send notification to each recipient
    for recipient in recipients:
        notify.send(
       
            recipient=recipient.user,  # Access the 'user' field of ChatSessionMember
            **notif_args,
            channels=['websocket']
        )

    return f"Notification sent for chat session {chat_session.id}"
