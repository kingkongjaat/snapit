import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max, Prefetch
from .models import Conversation, Message
from users.models import User


@login_required
def inbox(request):
    conversations = request.user.conversations.prefetch_related(
        'participants', 'messages'
    ).order_by('-updated_at')
    # Annotate unread counts
    conv_data = []
    for conv in conversations:
        other = conv.other_participant(request.user)
        last_msg = conv.messages.last()
        unread = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        conv_data.append({'conv': conv, 'other': other, 'last_msg': last_msg, 'unread': unread})
    return render(request, 'messaging/inbox.html', {'conv_data': conv_data})


@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('messaging:inbox')

    # Find or create conversation
    conv = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other_user)

    # Mark messages as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    chat_messages = conv.messages.select_related('sender').all()
    all_convs = request.user.conversations.prefetch_related('participants', 'messages').order_by('-updated_at')

    conv_data = []
    for c in all_convs:
        o = c.other_participant(request.user)
        last = c.messages.last()
        unread = c.messages.filter(is_read=False).exclude(sender=request.user).count()
        conv_data.append({'conv': c, 'other': o, 'last_msg': last, 'unread': unread})

    return render(request, 'messaging/conversation.html', {
        'conv': conv,
        'other_user': other_user,
        'chat_messages': chat_messages,
        'conv_data': conv_data,
    })


@login_required
@require_POST
def send_message(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id)
    if request.user not in conv.participants.all():
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Empty message'}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.save()  # updates updated_at
        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender.username,
                'created_at': msg.created_at.strftime('%H:%M'),
                'avatar': msg.sender.avatar.url if msg.sender.avatar else '',
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Bad request'}, status=400)


@login_required
def unread_message_count(request):
    # Count conversations that have at least one unread message (not individual messages)
    convs_with_unread = (
        request.user.conversations
        .filter(messages__is_read=False)
        .exclude(messages__sender=request.user)
        .distinct()
        .count()
    )
    return JsonResponse({'count': convs_with_unread})
