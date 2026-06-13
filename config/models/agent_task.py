from django.db  import models
from .agent_config import AgentConfig


class AgentTask(models.Model):
    """
    Inter-agent bus task. One agent creates a task, another agent executes it.
    Celery handles async execution and fires the callback on completion.
    """
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('running',     'Running'),
        ('done',        'Done'),
        ('failed',      'Failed'),
    ]

    TASK_TYPES = [
        ('research',    'Company Research'),
        ('draft',       'Outreach Draft'),
        ('enrich',      'Prospect Enrichment'),
        ('summarise',   'Summarise'),
        ('broadcast',   'Broadcast Content'),
    ]

    requesting_agent    = models.ForeignKey(AgentConfig, on_delete=models.CASCADE, related_name='requested_tasks')
    executing_agent     = models.ForeignKey(AgentConfig, on_delete=models.CASCADE, related_name='executing_tasks')
    task_type           = models.CharField(max_length=50, choices=TASK_TYPES)
    task_payload        = models.JSONField(default=dict, help_text='Input data for the executing agent.')
    result              = models.JSONField(null=True, blank=True, help_text='Output from the executing agent.')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    callback_config     = models.JSONField(default=dict, help_text='Where to send the result on completion. e.g. {"type": "whatsapp_group", "channel_id": "..."}')
    error_message       = models.TextField(blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    started_at          = models.DateTimeField(null=True, blank=True)
    completed_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Agent Task'
        verbose_name_plural = 'Agent Tasks'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.task_type} | {self.requesting_agent.name} → {self.executing_agent.name} | {self.status}'

    def mark_running(self):
        raise NotImplementedError('Set status to running and record started_at.')

    def mark_done(self, result: dict):
        raise NotImplementedError('Set status to done, store result, record completed_at.')

    def mark_failed(self, error: str):
        raise NotImplementedError('Set status to failed, store error_message, record completed_at.')

    def fire_callback(self):
        raise NotImplementedError('Send result to the channel specified in callback_config.')
