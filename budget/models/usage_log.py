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
