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
