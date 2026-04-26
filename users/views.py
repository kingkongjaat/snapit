from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import UserRegisterForm, UserEditForm
from .models import User, Follow


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SnapIt, {user.username}!')
            return redirect('core:home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def search_users(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'users': []})
    users = User.objects.filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
    )[:8]
    return JsonResponse({
        'users': [
            {
                'username': u.username,
                'bio': u.bio[:50] if u.bio else '',
                'avatar': u.avatar.url if u.avatar else '',
                'is_online': u.is_online(),
            }
            for u in users
        ]
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    posts = profile_user.posts.all()
    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'is_following': is_following,
        'posts': posts,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
    return JsonResponse({
        'following': following,
        'followers_count': target.followers.count()
    })


@login_required
def online_status(request, username):
    user = get_object_or_404(User, username=username)
    return JsonResponse({
        'is_online': user.is_online(),
        'last_seen': user.last_seen.isoformat()
    })


@login_required
def ping_status(request):
    """Called periodically by JS to keep status alive."""
    User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
    return JsonResponse({'ok': True})


@login_required
def profile_followers(request, username):
    target = get_object_or_404(User, username=username)
    followers = [
        {
            'username': f.follower.username,
            'avatar': f.follower.avatar.url if f.follower.avatar else '',
            'is_online': f.follower.is_online(),
        }
        for f in target.followers.select_related('follower').all()
    ]
    return JsonResponse({'users': followers})


@login_required
def profile_following(request, username):
    target = get_object_or_404(User, username=username)
    following = [
        {
            'username': f.following.username,
            'avatar': f.following.avatar.url if f.following.avatar else '',
            'is_online': f.following.is_online(),
        }
        for f in target.following.select_related('following').all()
    ]
    return JsonResponse({'users': following})

