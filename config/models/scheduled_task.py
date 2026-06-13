from django.db  import models
from .agent_config      import AgentConfig
from .channel_binding   import ChannelBinding


class ScheduledTask(models.Model):
    """
    Proactive task that fires on a time, cron schedule, or external signal.
    Handles reminders, recurring broadcasts, and signal-based alerts.
    """
    TRIGGER_TYPES = [
        ('time',        'One-time Time-based'),
        ('schedule',    'Recurring Cron Schedule'),
        ('signal',      'Signal-based'),
    ]

    agent               = models.ForeignKey(AgentConfig, on_delete=models.CASCADE, related_name='scheduled_tasks')
    channel_binding     = models.ForeignKey(ChannelBinding, on_delete=models.CASCADE, related_name='scheduled_tasks')
    trigger_type        = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    trigger_at          = models.DateTimeField(null=True, blank=True, help_text='For time-based triggers.')
    cron_expression     = models.CharField(max_length=100, blank=True, help_text='For recurring schedule triggers. e.g. 0 9 * * 1')
    signal_config       = models.JSONField(default=dict, help_text='For signal-based triggers. Defines what signal to watch.')
    task_prompt         = models.TextField(help_text='What to do or say when the trigger fires.')
    created_by          = models.CharField(max_length=100, help_text='Phone number of the sender who created this task.')
    requires_context    = models.BooleanField(default=False, help_text='If True, fetch fresh context at fire time before sending.')
    context_query       = models.TextField(blank=True, help_text='CRM or research query to run at fire time if requires_context is True.')
    requires_approval   = models.BooleanField(default=False, help_text='If True, send preview to admin before posting.')
    is_active           = models.BooleanField(default=True)
    last_run            = models.DateTimeField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Scheduled Task'
        verbose_name_plural = 'Scheduled Tasks'
        ordering            = ['trigger_at']

    def __str__(self):
        return f'{self.trigger_type} | {self.agent.name} | {self.channel_binding}'

    def is_due(self) -> bool:
        raise NotImplementedError('Return True if this task should fire now.')

    def execute(self):
        raise NotImplementedError('Run the task — fetch context if needed, generate content, send to channel.')

    def fetch_context(self) -> str:
        raise NotImplementedError('Run context_query and return result as string. Only called if requires_context is True.')
