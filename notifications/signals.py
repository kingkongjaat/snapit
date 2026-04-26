from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from posts.models import Like, Comment, Post
from users.models import Follow, User
import re


def _get_mentions(text):
    return re.findall(r'@(\w+)', text)


@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.author:
        Notification.objects.create(
            recipient=instance.post.author,
            sender=instance.user,
            notification_type='like',
            post_id=instance.post.id
        )


@receiver(post_save, sender=Comment)
def notify_comment_and_mentions(sender, instance, created, **kwargs):
    if not created:
        return

    # Notify post author about comment (only top-level)
    if instance.parent is None and instance.author != instance.post.author:
        Notification.objects.create(
            recipient=instance.post.author,
            sender=instance.author,
            notification_type='comment',
            post_id=instance.post.id,
            comment_id=instance.id
        )

    # Notify parent comment author about reply
    if instance.parent is not None and instance.author != instance.parent.author:
        Notification.objects.create(
            recipient=instance.parent.author,
            sender=instance.author,
            notification_type='reply',
            post_id=instance.post.id,
            comment_id=instance.id
        )

    # Notify mentioned users in comment
    for username in _get_mentions(instance.content):
        try:
            mentioned_user = User.objects.get(username=username)
            if mentioned_user != instance.author:
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=instance.author,
                    notification_type='comment_mention',
                    post_id=instance.post.id,
                    comment_id=instance.id
                )
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=Post)
def notify_post_mentions(sender, instance, created, **kwargs):
    if not created:
        return
    for username in _get_mentions(instance.content):
        try:
            mentioned_user = User.objects.get(username=username)
            if mentioned_user != instance.author:
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=instance.author,
                    notification_type='mention',
                    post_id=instance.id
                )
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow'
        )
