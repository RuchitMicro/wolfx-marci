#!/bin/bash
set -euo pipefail

APP="budget"

rm -f $APP/models.py $APP/views.py

mkdir -p $APP/models
mkdir -p $APP/views

# ── models/__init__.py ──
cat > $APP/models/__init__.py << 'EOF'
from .usage_log import TokenUsageLog

__all__ = ['TokenUsageLog']
EOF

# ── models/usage_log.py ──
cat > $APP/models/usage_log.py << 'EOF'
from django.db import models


class TokenUsageLog(models.Model):
    """
    Daily token usage record per agent.
    Written after every LLM call. Used by dashboard and alerting.
    """
    agent_id        = models.IntegerField(db_index=True)
    agent_name      = models.CharField(max_length=100)
    date            = models.DateField(db_index=True)
    intent          = models.CharField(max_length=50, blank=True)
    model_used      = models.CharField(max_length=100)
    tokens_input    = models.IntegerField(default=0)
    tokens_output   = models.IntegerField(default=0)
    tokens_total    = models.IntegerField(default=0)
    estimated_cost  = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Token Usage Log'
        verbose_name_plural = 'Token Usage Logs'
        ordering            = ['-created_at']
        indexes             = [
            models.Index(fields=['agent_id', 'date']),
        ]

    def __str__(self):
        return f'{self.agent_name} — {self.date} — {self.tokens_total} tokens'

    @classmethod
    def get_daily_total(cls, agent_id: int, date) -> int:
        raise NotImplementedError('Return total tokens used by this agent today.')

    @classmethod
    def get_monthly_total(cls, agent_id: int, year: int, month: int) -> int:
        raise NotImplementedError('Return total tokens used by this agent this month.')

    @classmethod
    def get_estimated_cost_today(cls, agent_id: int) -> float:
        raise NotImplementedError('Return estimated USD cost for today.')
EOF

# ── enforcer.py ──
cat > $APP/enforcer.py << 'EOF'
class BudgetEnforcer:
    """
    Checks token budget before every LLM call using Redis counters.
    Raises BudgetExceededError if any limit is hit.
    Records usage after every successful LLM call.
    """

    def __init__(self, agent_config, redis_client):
        self.config = agent_config
        self.redis  = redis_client

    def check_or_raise(self):
        raise NotImplementedError(
            'Check Redis counters for agent daily and monthly token limits. '
            'Raise BudgetExceededError with a friendly message if any limit is hit.'
        )

    def record_usage(self, tokens_input: int, tokens_output: int, model: str, intent: str = ''):
        raise NotImplementedError(
            'Increment Redis counters for agent daily and monthly usage. '
            'Write TokenUsageLog record. '
            'Check if alert threshold (alert_at_pct) is crossed and fire alert if so.'
        )

    def fire_alert(self, pct_used: float):
        raise NotImplementedError(
            'Send WhatsApp message to admin number warning that X% of daily budget is consumed. '
            'Only fire once per threshold crossing — not on every call.'
        )

    def get_daily_usage(self) -> int:
        raise NotImplementedError('Return current daily token count from Redis.')

    def get_monthly_usage(self) -> int:
        raise NotImplementedError('Return current monthly token count from Redis.')


class BudgetExceededError(Exception):
    """Raised when an agent has hit its token budget limit."""
    pass
EOF

# ── tracker.py ──
cat > $APP/tracker.py << 'EOF'
class UsageTracker:
    """
    Reads usage data from Redis and TokenUsageLog for the dashboard.
    No writes — read-only view of budget state.
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    def get_all_agents_today(self) -> list:
        raise NotImplementedError(
            'Return list of dicts: [{agent_id, agent_name, tokens_today, limit, pct_used, est_cost}] '
            'for all active agents.'
        )

    def get_global_today(self) -> dict:
        raise NotImplementedError('Return combined token usage across all agents for today.')

    def get_monthly_summary(self) -> dict:
        raise NotImplementedError('Return monthly token usage and cost per agent from TokenUsageLog.')
EOF

# ── views/__init__.py ──
cat > $APP/views/__init__.py << 'EOF'
from .usage_log import TokenUsageLogView

__all__ = ['TokenUsageLogView']
EOF

# ── views/usage_log.py ──
cat > $APP/views/usage_log.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from budget.models import TokenUsageLog


class TokenUsageLogView(GenericCRUDView):
    model               = TokenUsageLog
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── urls.py ──
cat > $APP/urls.py << 'EOF'
from django.urls import path
from .views import TokenUsageLogView

urlpatterns = [
    path('usage-logs/', TokenUsageLogView.as_view(), name='usage-log-list'),
]
EOF

# ── admin.py ──
cat > $APP/admin.py << 'EOF'
from django.contrib import admin
from .models import TokenUsageLog


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display    = ['agent_name', 'date', 'model_used', 'intent', 'tokens_total', 'estimated_cost', 'created_at']
    list_filter     = ['agent_name', 'model_used', 'date']
    ordering        = ['-created_at']
EOF

# ── apps.py ──
cat > $APP/apps.py << 'EOF'
from django.apps import AppConfig


class BudgetConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'budget'
    verbose_name        = 'Budget & Usage'
EOF

echo ""
echo "budget app structure created successfully."