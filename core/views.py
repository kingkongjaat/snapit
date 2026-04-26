from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from posts.models import Post
from posts.forms import PostForm


def home(request):
    # Show landing page to unauthenticated users
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')

    posts = Post.objects.select_related('author').prefetch_related('likes', 'comments')
    following_users = request.user.following.values_list('following', flat=True)
    posts = posts.filter(
        Q(privacy='public') |
        Q(author=request.user) |
        (Q(privacy='followers') & Q(author__in=following_users)) |
        (Q(privacy='specific') & Q(allowed_users=request.user))
    ).distinct()

    posts = list(posts)
    for post in posts:
        post.user_liked = post.likes.filter(user=request.user).exists()
        post.top_likers = list(post.likes.select_related('user').values_list('user__username', flat=True)[:3])

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post shared!')
            return redirect('core:home')
    else:
        form = PostForm()

    todos = request.user.todos.all()

    return render(request, 'core/feed.html', {'posts': posts, 'form': form, 'todos': todos})


import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Todo

@login_required
@require_POST
def add_todo(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        if text:
            todo = Todo.objects.create(user=request.user, text=text)
            return JsonResponse({'ok': True, 'id': todo.id, 'text': todo.text})
        return JsonResponse({'ok': False, 'error': 'Empty text'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def toggle_todo(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id, user=request.user)
        todo.is_completed = not todo.is_completed
        todo.save(update_fields=['is_completed'])
        return JsonResponse({'ok': True, 'is_completed': todo.is_completed})
    except Todo.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)

@login_required
@require_POST
def delete_todo(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id, user=request.user)
        todo.delete()
        return JsonResponse({'ok': True})
    except Todo.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)
