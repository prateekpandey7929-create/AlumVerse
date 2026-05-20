from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import User, Notification
from .models import Message

# Inbox (Conversation List)
@login_required
def inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by("-created_at")

    conversations = {}

    for msg in messages:

        if msg.sender == request.user:
            other = msg.receiver
        else:
            other = msg.sender

        if other.id not in conversations:
            conversations[other.id] = {
                "user": other,
                "last_message": msg.message
            }

    return render(
        request,
        "inbox.html",
        {"conversations": conversations.values()}
    )


# Chat System
@login_required
def send_message(request, user_id):
    receiver = User.objects.get(id=user_id)

    if request.method == "POST":

        text = request.POST.get("message")

        if text:

            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                message=text
            )

            # Create notification only for receiver
            if receiver != request.user:
                Notification.objects.create(
                    user=receiver,
                    message=f"New message from {request.user.username}"
                )

        return redirect(f"/messages/{user_id}/")

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by("created_at")

    # Mark received messages as read
    Message.objects.filter(
        sender=receiver,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "chat.html",
        {
            "messages": messages,
            "receiver": receiver
        }
    )
