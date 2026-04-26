from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserSettings(models.Model):
    PRIVACY_CHOICES = (
        ('everyone', 'Everyone'),
        ('followers', 'Followers Only'),
        ('nobody', 'Nobody'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_settings')
    # Notifications
    notify_likes = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    notify_follows = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    # Privacy
    show_online_status = models.BooleanField(default=True)
    allow_messages_from = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    private_account = models.BooleanField(default=False)
    # Theme stored here too (dark / light)
    theme = models.CharField(max_length=10, default='dark')

    def __str__(self):
        return f"Settings for {self.user.username}"


class Report(models.Model):
    REASON_CHOICES = (
        ('spam', 'Spam'),
        ('abuse', 'Abusive Content'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Material'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    reported_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports_against')
    reported_post_id = models.IntegerField(null=True, blank=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.reporter} ({self.reason})"


class Feedback(models.Model):
    CATEGORY_CHOICES = (
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('general', 'General Feedback'),
        ('other', 'Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username}: {self.subject[:30]}"

class BannedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban_record')
    banned_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} banned on {self.banned_at.strftime('%Y-%m-%d')}"
