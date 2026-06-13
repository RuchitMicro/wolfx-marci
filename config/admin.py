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
