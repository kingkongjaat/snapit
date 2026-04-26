from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def last_message(self):
        return self.messages.last()

    def __str__(self):
        return f"Conversation {self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender} in conv {self.conversation_id}"
