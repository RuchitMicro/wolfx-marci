from django.db import models


class ConversationLog(models.Model):
    """
    Layer 1 — Short-term in-session conversation history.
    One row per message exchanged in a channel session.
    """
    ROLE_CHOICES = [
        ('user',      'User'),
        ('assistant', 'Assistant'),
    ]

    channel_id      = models.CharField(max_length=100, help_text='WhatsApp group ID or Slack channel ID.')
    sender          = models.CharField(max_length=100, blank=True, help_text='Sender phone number.')
    sender_name     = models.CharField(max_length=100, blank=True, help_text='Resolved display name.')
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message         = models.TextField()
    intent          = models.CharField(max_length=50, blank=True, help_text='Classified intent of this message.')
    tool_calls      = models.JSONField(default=list, help_text='Tools called during this turn.')
    tokens_used     = models.IntegerField(default=0)
    sql_used        = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Conversation Log'
        verbose_name_plural = 'Conversation Logs'
        ordering            = ['created_at']
        indexes             = [
            models.Index(fields=['channel_id', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f'[{self.role}] {self.channel_id} — {self.created_at:%d %b %Y %H:%M}'

    @classmethod
    def get_recent(cls, channel_id: str, window: int = 10):
        raise NotImplementedError('Return the last N messages for this channel ordered by created_at.')

    @classmethod
    def get_recent_for_sender(cls, channel_id: str, sender: str, window: int = 5):
        raise NotImplementedError('Return the last N messages from this specific sender in this channel.')
