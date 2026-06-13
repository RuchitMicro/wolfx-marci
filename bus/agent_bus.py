from config.models import AgentTask, AgentConfig


class AgentBus:
    """
    Inter-agent communication bus.
    Creates AgentTask records and dispatches them to Celery for async execution.
    Requesting agents never block — they create a task and reply immediately.
    """

    def create_task(
        self,
        task_type: str,
        executing_agent_type: str,
        payload: dict,
        requesting_agent,
        callback_config: dict,
    ) -> AgentTask:
        raise NotImplementedError(
            'Create an AgentTask record. '
            'Look up executing agent by agent_type. '
            'Dispatch to Celery via tasks.execute_agent_task. '
            'Return the created AgentTask.'
        )

    def get_result(self, task_id: int) -> dict:
        raise NotImplementedError('Return result from AgentTask if status is done, else return None.')

    def cancel_task(self, task_id: int):
        raise NotImplementedError('Mark AgentTask as failed with error "cancelled by requester".')
