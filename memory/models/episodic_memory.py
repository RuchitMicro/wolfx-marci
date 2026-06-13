from django.db import models


class EpisodicMemory(models.Model):
    """
    Layer 2 — Medium-term summarised past sessions.
    Created by a background Celery task after each conversation ends.
    Summarises key points, decisions, and context from a session.
    """
    channel_id      = models.CharField(max_length=100)
    sender          = models.CharField(max_length=100, blank=True, help_text='Phone number if user-scoped, empty if group-scoped.')
    scope           = models.CharField(max_length=20, choices=[
        ('group',   'Group'),
        ('user',    'User'),
    ], default='group')
    summary         = models.TextField(help_text='LLM-generated summary of the session.')
    key_entities    = models.JSONField(default=list, help_text='Company names, person names mentioned.')
    key_decisions   = models.JSONField(default=list, help_text='Decisions or action items from the session.')
    session_start   = models.DateTimeField()
    session_end     = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Episodic Memory'
        verbose_name_plural = 'Episodic Memories'
        ordering            = ['-session_end']
        indexes             = [
            models.Index(fields=['channel_id', 'scope']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f'Episode {self.channel_id} — {self.session_end:%d %b %Y}'

    @classmethod
    def get_recent_for_channel(cls, channel_id: str, limit: int = 5):
        raise NotImplementedError('Return recent episodic memories for this channel.')

    @classmethod
    def get_recent_for_sender(cls, sender: str, limit: int = 3):
        raise NotImplementedError('Return recent episodic memories for this sender across all channels.')

    @classmethod
    def create_from_conversation(cls, channel_id: str, sender: str, messages: list):
        raise NotImplementedError('Summarise a list of ConversationLog messages and create an EpisodicMemory record.')
