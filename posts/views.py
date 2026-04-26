import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import Post, Like, Comment, CommentLike
from users.models import User


# ─── Update last seen on every request ─────────────────────────────────────
def update_last_seen(request):
    if request.user.is_authenticated:
        User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())


@login_required
@require_POST
def toggle_like(request, post_id):
    update_last_seen(request)
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    likers = list(post.likes.select_related('user').values('user__username', 'user__avatar')[:6])
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
        'likers': likers
    })


@login_required
@require_GET
def post_likers(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    likers = [
        {'username': l.user.username, 'avatar': l.user.avatar.url if l.user.avatar else ''}
        for l in post.likes.select_related('user').all()
    ]
    return JsonResponse({'likers': likers})


@login_required
@require_POST
def add_comment(request, post_id):
    update_last_seen(request)
    post = get_object_or_404(Post, id=post_id)
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        if not content:
            return JsonResponse({'success': False, 'error': 'Empty comment'}, status=400)

        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'avatar': comment.author.avatar.url if comment.author.avatar else '',
                'content': comment.content,
                'created_at': 'Just now',
                'parent_id': parent_id,
                'is_online': comment.author.is_online(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False}, status=400)


@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    update_last_seen(request)
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': comment.likes.count()})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    top_comments = post.comments.filter(parent=None).prefetch_related('replies__author', 'likes')
    context = {
        'post': post,
        'top_comments': top_comments,
        'user_liked': post.likes.filter(user=request.user).exists(),
    }
    return render(request, 'posts/post_detail.html', context)
