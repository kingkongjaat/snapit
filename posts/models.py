import re
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers', 'Followers Only'),
        ('specific', 'Specific Users'),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, help_text="What's on your mind?")
    code_snippet = models.TextField(blank=True, help_text="Share some code!")
    code_language = models.CharField(max_length=30, default='python', blank=True)
    media = models.FileField(upload_to='post_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    allowed_users = models.ManyToManyField(User, related_name='allowed_posts', blank=True)
    tagged_users = models.ManyToManyField(User, related_name='tagged_in_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def extract_mentions(self):
        """Return list of @mentioned usernames in content."""
        return re.findall(r'@(\w+)', self.content)

    def __str__(self):
        return f"Post by {self.author} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def extract_mentions(self):
        return re.findall(r'@(\w+)', self.content)

    def __str__(self):
        return f"Comment by {self.author} on post {self.post.id}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_given')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} likes post {self.post.id}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes_given')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')
