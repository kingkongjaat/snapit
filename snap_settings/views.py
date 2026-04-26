import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages
from .models import UserSettings, Report, Feedback
from users.models import User


def _get_or_create_settings(user):
    obj, _ = UserSettings.objects.get_or_create(user=user)
    return obj


@login_required
def settings_page(request):
    user_settings = _get_or_create_settings(request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'notifications':
            user_settings.notify_likes = 'notify_likes' in request.POST
            user_settings.notify_comments = 'notify_comments' in request.POST
            user_settings.notify_follows = 'notify_follows' in request.POST
            user_settings.notify_mentions = 'notify_mentions' in request.POST
            user_settings.notify_messages = 'notify_messages' in request.POST
            user_settings.save()
            django_messages.success(request, 'Notification settings saved!')
        elif action == 'privacy':
            user_settings.show_online_status = 'show_online_status' in request.POST
            user_settings.private_account = 'private_account' in request.POST
            user_settings.allow_messages_from = request.POST.get('allow_messages_from', 'everyone')
            user_settings.save()
            django_messages.success(request, 'Privacy settings saved!')
        elif action == 'theme':
            user_settings.theme = request.POST.get('theme', 'dark')
            user_settings.save()
            return JsonResponse({'ok': True, 'theme': user_settings.theme})
        return redirect('snap_settings:settings')
    return render(request, 'snap_settings/settings.html', {'user_settings': user_settings})


@login_required
@require_POST
def submit_report(request):
    try:
        data = json.loads(request.body)
        Report.objects.create(
            reporter=request.user,
            reported_user=User.objects.filter(username=data.get('username')).first(),
            reported_post_id=data.get('post_id'),
            reason=data.get('reason', 'other'),
            description=data.get('description', ''),
        )
        return JsonResponse({'ok': True, 'message': 'Report submitted. We will review it shortly.'})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def submit_feedback(request):
    try:
        data = json.loads(request.body)
        Feedback.objects.create(
            user=request.user,
            category=data.get('category', 'general'),
            subject=data.get('subject', ''),
            message=data.get('message', ''),
        )
        return JsonResponse({'ok': True, 'message': 'Thank you for your feedback!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)}, status=400)
