from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='covers/', null=True, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    last_seen = models.DateTimeField(default=timezone.now)

    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(minutes=5)

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"
