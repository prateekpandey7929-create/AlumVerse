from .models import Notification
from messaging.models import Message

def notification_count(request):
    if request.user.is_authenticated:

        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        messages = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        return {
            "notification_count": notifications,
            "unread_messages": messages
        }

    return {
        "notification_count": 0,
        "unread_messages": 0
    }
