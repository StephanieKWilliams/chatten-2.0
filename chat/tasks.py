from celery import shared_task
from notifications.signals import notify
from .models import ChatSession, ChatSessionMember
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from channels.layers import get_channel_layer

@shared_task
def send_chat_notification(chat_session_id, user_id):
    # Fetch the user model
    User = get_user_model()

    try:
        # Fetch the chat session and user details
        chat_session = ChatSession.objects.get(id=chat_session_id)
        user = User.objects.get(id=user_id)
    except (ChatSession.DoesNotExist, User.DoesNotExist) as e:
        return f"Error: {e}"

    # Prepare notification arguments
    notif_args = {
        'sender': user,  # The actor (sender)
        'recipient': None,  # Placeholder, will be set for each recipient in the loop
        'source_display_name': user.get_full_name(),
        'verb':'Sent',
        'category': 'chat',
        
        'obj': chat_session.id,
        'level':'success',
        'short_description': 'You have a new message'

    }

    # Identify the recipients (all members in the chat session except the sender)
    try:
        recipients = ChatSessionMember.objects.filter(chat_session=chat_session).exclude(user=user)
    except ChatSessionMember.DoesNotExist:
        return "Error: No members found in the chat session."

    # Send notification to each recipient
    for member in recipients:
        notif_args['recipient'] = member.user  # Set the recipient
        # notify.send(
        #     **notif_args,
        #     countdown=0,
        #     channels=['websocket']
        # )
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f'chat_{chat_session.id}',  # Group name based on chat session ID
            {
                'type': 'chat_notification',  # The message type to handle in the consumer
                'message': notif_args['short_description'],  # Example message content
            }
        )
    return f"Notification sent for chat session {chat_session.id}"
