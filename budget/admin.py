from django.contrib import admin
from .models import TokenUsageLog


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display    = ['agent_name', 'date', 'model_used', 'intent', 'tokens_total', 'estimated_cost', 'created_at']
    list_filter     = ['agent_name', 'model_used', 'date']
    ordering        = ['-created_at']
