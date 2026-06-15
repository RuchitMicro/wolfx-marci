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
    enabled_tools           = models.JSONField(default=list, help_text='List of tool names this agent can use.', blank=True)
    memory_layers           = models.JSONField(default=list, help_text='Which memory layers to retrieve: conversation, episodic, semantic, entity.')
    sender_name_map         = models.JSONField(default=dict, help_text='Phone number → display name map. Auto-populated via pushname.', blank=True)
    authorised_numbers      = models.TextField(blank=True, help_text='Comma-separated authorised sender numbers. Empty = allow all.')
    context_window          = models.PositiveIntegerField(default=10)
    memory_staleness_days   = models.IntegerField(default=7, help_text='Days before cached research is considered stale.')
    daily_token_limit       = models.IntegerField(default=50000)
    monthly_token_limit     = models.IntegerField(default=500000)
    max_tokens_per_call     = models.IntegerField(default=2000)
    max_iterations          = models.IntegerField(default=5, help_text='Max LangGraph ReAct iterations per request.')
    alert_at_pct            = models.IntegerField(default=80, help_text='Alert when this % of daily token budget is consumed.')
    tool_model_map          = models.JSONField(default=dict, help_text='Tool name → model name override. e.g. {"crm_query": "gpt-5-nano"}', blank=True)
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
