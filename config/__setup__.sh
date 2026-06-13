#!/bin/bash
set -euo pipefail

APP="config"

# ── Remove default models.py and views.py ──
rm -f $APP/models.py $APP/views.py

# ── Create directory structure ──
mkdir -p $APP/models
mkdir -p $APP/views

# ── models/__init__.py ──
cat > $APP/models/__init__.py << 'EOF'
from .global_prompt     import GlobalPrompt
from .agent_config      import AgentConfig
from .channel_binding   import ChannelBinding
from .agent_task        import AgentTask
from .scheduled_task    import ScheduledTask

__all__ = [
    'GlobalPrompt',
    'AgentConfig',
    'ChannelBinding',
    'AgentTask',
    'ScheduledTask',
]
EOF

# ── models/global_prompt.py ──
cat > $APP/models/global_prompt.py << 'EOF'
from django.db import models


class GlobalPrompt(models.Model):
    """
    Versioned global prompt applied to all agents as the base non-negotiable layer.
    Only one instance should be active at a time.
    """
    version     = models.CharField(max_length=20, unique=True)
    content     = models.TextField(help_text='Non-negotiable instructions applied to all agents.')
    is_active   = models.BooleanField(default=False, help_text='Only one GlobalPrompt should be active at a time.')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Global Prompt'
        verbose_name_plural = 'Global Prompts'
        ordering            = ['-created_at']

    def __str__(self):
        return f'v{self.version} ({"active" if self.is_active else "inactive"})'

    def save(self, *args, **kwargs):
        raise NotImplementedError('Override save() to enforce single active instance.')

    @classmethod
    def get_active(cls):
        raise NotImplementedError('Return the currently active GlobalPrompt instance.')
EOF

# ── models/agent_config.py ──
cat > $APP/models/agent_config.py << 'EOF'
from django.db import models


class AgentConfig(models.Model):
    """
    Per-agent configuration. One row = one agent instance.
    Controls prompts, tools, memory layers, budget, and behaviour.
    """
    name                    = models.CharField(max_length=100)
    agent_type              = models.CharField(max_length=50, help_text='Maps to a Python class in agents/registry.py')
    system_prompt           = models.TextField(help_text='Agent-specific capabilities and knowledge.')
    personality_prompt      = models.TextField(help_text='Tone, relationship style, and communication rules.')
    enabled_tools           = models.JSONField(default=list, help_text='List of tool names this agent can use.')
    memory_layers           = models.JSONField(default=list, help_text='Which memory layers to retrieve: conversation, episodic, semantic, entity.')
    sender_name_map         = models.JSONField(default=dict, help_text='Phone number → display name map. Auto-populated via pushname.')
    authorised_numbers      = models.TextField(blank=True, help_text='Comma-separated authorised sender numbers. Empty = allow all.')
    context_window          = models.PositiveIntegerField(default=10)
    memory_staleness_days   = models.IntegerField(default=7, help_text='Days before cached research is considered stale.')
    daily_token_limit       = models.IntegerField(default=50000)
    monthly_token_limit     = models.IntegerField(default=500000)
    max_tokens_per_call     = models.IntegerField(default=2000)
    max_iterations          = models.IntegerField(default=5, help_text='Max LangGraph ReAct iterations per request.')
    alert_at_pct            = models.IntegerField(default=80, help_text='Alert when this % of daily token budget is consumed.')
    tool_model_map          = models.JSONField(default=dict, help_text='Tool name → model name override. e.g. {"crm_query": "gpt-5-nano"}')
    is_active               = models.BooleanField(default=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Agent Config'
        verbose_name_plural = 'Agent Configs'
        ordering            = ['name']

    def __str__(self):
        return f'{self.name} ({self.agent_type})'

    def get_global_prompt(self):
        raise NotImplementedError('Return the currently active GlobalPrompt content as a string.')

    def get_full_prompt(self):
        raise NotImplementedError('Return concatenated global + system + personality prompt.')

    def is_sender_authorised(self, phone_number: str) -> bool:
        raise NotImplementedError('Return True if sender is allowed to interact with this agent.')

    def resolve_sender_name(self, phone_number: str) -> str:
        raise NotImplementedError('Return display name for phone_number from sender_name_map or return number as fallback.')
EOF

# ── models/channel_binding.py ──
cat > $APP/models/channel_binding.py << 'EOF'
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
EOF

# ── models/agent_task.py ──
cat > $APP/models/agent_task.py << 'EOF'
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
EOF

# ── models/scheduled_task.py ──
cat > $APP/models/scheduled_task.py << 'EOF'
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
EOF

# ── views/__init__.py ──
cat > $APP/views/__init__.py << 'EOF'
from .global_prompt     import GlobalPromptView
from .agent_config      import AgentConfigView
from .channel_binding   import ChannelBindingView
from .agent_task        import AgentTaskView
from .scheduled_task    import ScheduledTaskView

__all__ = [
    'GlobalPromptView',
    'AgentConfigView',
    'ChannelBindingView',
    'AgentTaskView',
    'ScheduledTaskView',
]
EOF

# ── views/global_prompt.py ──
cat > $APP/views/global_prompt.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from config.models import GlobalPrompt


class GlobalPromptView(GenericCRUDView):
    model           = GlobalPrompt
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions

    def activate(self, request, pk):
        raise NotImplementedError('Deactivate all other prompts and activate this one.')
EOF

# ── views/agent_config.py ──
cat > $APP/views/agent_config.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from config.models import AgentConfig


class AgentConfigView(GenericCRUDView):
    model               = AgentConfig
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/channel_binding.py ──
cat > $APP/views/channel_binding.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from config.models import ChannelBinding


class ChannelBindingView(GenericCRUDView):
    model               = ChannelBinding
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/agent_task.py ──
cat > $APP/views/agent_task.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from config.models import AgentTask


class AgentTaskView(GenericCRUDView):
    model               = AgentTask
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/scheduled_task.py ──
cat > $APP/views/scheduled_task.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from config.models import ScheduledTask


class ScheduledTaskView(GenericCRUDView):
    model               = ScheduledTask
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── urls.py ──
cat > $APP/urls.py << 'EOF'
from django.urls import path
from .views import (
    GlobalPromptView,
    AgentConfigView,
    ChannelBindingView,
    AgentTaskView,
    ScheduledTaskView,
)

urlpatterns = [
    path('global-prompts/',     GlobalPromptView.as_view(),     name='global-prompt-list'),
    path('agent-configs/',      AgentConfigView.as_view(),      name='agent-config-list'),
    path('channel-bindings/',   ChannelBindingView.as_view(),   name='channel-binding-list'),
    path('agent-tasks/',        AgentTaskView.as_view(),        name='agent-task-list'),
    path('scheduled-tasks/',    ScheduledTaskView.as_view(),    name='scheduled-task-list'),
]
EOF

# ── admin.py ──
cat > $APP/admin.py << 'EOF'
from django.contrib import admin
from .models import (
    GlobalPrompt,
    AgentConfig,
    ChannelBinding,
    AgentTask,
    ScheduledTask,
)


@admin.register(GlobalPrompt)
class GlobalPromptAdmin(admin.ModelAdmin):
    list_display    = ['version', 'is_active', 'created_at']
    list_filter     = ['is_active']
    ordering        = ['-created_at']


@admin.register(AgentConfig)
class AgentConfigAdmin(admin.ModelAdmin):
    list_display    = ['name', 'agent_type', 'is_active', 'updated_at']
    list_filter     = ['is_active', 'agent_type']
    ordering        = ['name']


@admin.register(ChannelBinding)
class ChannelBindingAdmin(admin.ModelAdmin):
    list_display    = ['channel_type', 'channel_id', 'agent', 'is_active']
    list_filter     = ['channel_type', 'is_active']


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display    = ['task_type', 'requesting_agent', 'executing_agent', 'status', 'created_at']
    list_filter     = ['status', 'task_type']
    ordering        = ['-created_at']


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display    = ['trigger_type', 'agent', 'channel_binding', 'is_active', 'last_run']
    list_filter     = ['trigger_type', 'is_active']
    ordering        = ['trigger_at']
EOF

# ── apps.py ──
cat > $APP/apps.py << 'EOF'
from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'config'
    verbose_name        = 'Agent Configuration'
EOF

echo ""
echo "config app structure created successfully."