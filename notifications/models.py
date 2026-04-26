from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'liked your post'),
        ('comment', 'commented on your post'),
        ('reply', 'replied to your comment'),
        ('follow', 'started following you'),
        ('mention', 'mentioned you in a post'),
        ('comment_mention', 'mentioned you in a comment'),
    )

    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    post_id = models.IntegerField(null=True, blank=True)
    comment_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_message(self):
        return dict(self.NOTIFICATION_TYPES).get(self.notification_type, '')

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.notification_type})"
