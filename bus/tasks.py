"""
bus/tasks.py

Celery tasks for the agent bus.
Handles async dispatch of WhatsApp messages to agents.
Handles scheduled task execution.
Handles session summarisation.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def dispatch_whatsapp_message(self, payload: dict):
    """
    Celery task — dispatches an incoming WhatsApp message to the channel handler.
    Called by WhatsAppWebhookView immediately on webhook receipt.
    Retries up to 3 times on failure with 5 second delay.
    """
    try:
        from channels.implementations.whatsapp import WhatsAppChannel
        channel = WhatsAppChannel()
        channel.dispatch(payload)
    except Exception as exc:
        logger.exception(f'[dispatch_whatsapp_message] Error: {exc}')
        raise self.retry(exc=exc)


@shared_task
def execute_agent_task(agent_task_id: int):
    """
    Celery task — executes an AgentTask from the inter-agent bus.
    Loads the executing agent, runs it, stores result, fires callback.
    TODO: implement when AgentBus is built.
    """
    raise NotImplementedError(
        '1. Load AgentTask by agent_task_id. '
        '2. Mark as running. '
        '3. Load executing agent from registry. '
        '4. Run agent with task_payload. '
        '5. Mark as done with result. '
        '6. Fire callback via task.fire_callback(). '
        'On exception: mark as failed, retry if max_retries not hit.'
    )


@shared_task
def fire_scheduled_tasks():
    """
    Celery Beat task — runs every minute.
    Checks for due ScheduledTasks and executes them.
    TODO: implement when ScheduledTask.execute() is built.
    """
    raise NotImplementedError(
        '1. Query ScheduledTask where trigger_type=time, trigger_at <= now, is_active=True. '
        '2. For each due task: call task.execute(). '
        '3. Update last_run. '
        '4. Deactivate one-time tasks after execution.'
    )


@shared_task
def summarise_sessions():
    """
    Celery Beat task — runs every hour.
    Summarises recent conversation activity into EpisodicMemory.
    TODO: implement when MemoryManager.summarise_session() is built.
    """
    raise NotImplementedError(
        '1. Find channels with ConversationLog entries in the last hour. '
        '2. For each: call MemoryManager.summarise_session(). '
    )