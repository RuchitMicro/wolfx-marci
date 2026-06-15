from django.db  import models
from .agent_config import AgentConfig


class ChannelBinding(models.Model):
    """
    Maps a channel (WhatsApp group, Slack channel) to an AgentConfig.
    One channel maps to exactly one agent. One agent can serve multiple channels.
    """
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('slack',    'Slack'),
    ]

    channel_type    = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    channel_id      = models.CharField(max_length=100, help_text='WhatsApp group ID or Slack channel ID.')
    agent           = models.ForeignKey(AgentConfig, on_delete=models.CASCADE, related_name='channel_bindings')
    bot_number      = models.CharField(max_length=50, help_text='Bot number used to detect @mentions.')
    api_base        = models.CharField(max_length=200, help_text='MCP server base URL for this channel.')
    api_key = models.CharField(
        max_length=200,
        blank=True,
        help_text='API key for the MCP server. e.g. wweb-mcp Bearer token.'
    )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Channel Binding'
        verbose_name_plural = 'Channel Bindings'
        unique_together     = [('channel_type', 'channel_id')]

    def __str__(self):
        return f'{self.channel_type}:{self.channel_id} → {self.agent.name}'

    @classmethod
    def get_for_channel(cls, channel_type: str, channel_id: str):
        raise NotImplementedError('Return the active ChannelBinding for this channel_type + channel_id combination.')
