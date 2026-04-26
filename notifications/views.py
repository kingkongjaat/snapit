from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    notifs = request.user.notifications.select_related('sender').all()[:50]
    return render(request, 'notifications/notifications.html', {'notifications': notifs})


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


@login_required
def unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    recent = []
    for n in request.user.notifications.select_related('sender').filter(is_read=False)[:5]:
        recent.append({
            'id': n.id,
            'sender': n.sender.username,
            'avatar': n.sender.avatar.url if n.sender.avatar else '',
            'message': n.get_message(),
            'type': n.notification_type,
            'post_id': n.post_id,
            'comment_id': n.comment_id,
            'created_at': n.created_at.strftime('%b %d, %H:%M'),
            'is_online': n.sender.is_online(),
        })
    return JsonResponse({'count': count, 'recent': recent})

from django.shortcuts import get_object_or_404, redirect

@login_required
def redirect_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    
    if notif.post_id:
        url = f"/posts/{notif.post_id}/"
        if notif.comment_id:
            url += f"#comment-{notif.comment_id}"
        return redirect(url)
    return redirect('users:profile', username=notif.sender.username)
