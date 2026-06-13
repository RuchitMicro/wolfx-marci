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
