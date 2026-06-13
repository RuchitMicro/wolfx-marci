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
