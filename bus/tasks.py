from celery import shared_task


@shared_task(bind=True, max_retries=3)
def execute_agent_task(self, agent_task_id: int):
    """
    Celery task that executes an AgentTask.
    Loads the executing agent, runs it, stores result, fires callback.
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
    """
    raise NotImplementedError(
        '1. Query ScheduledTask where trigger_type=time, trigger_at <= now, is_active=True, last_run is None. '
        '2. For each due task: call task.execute(). '
        '3. Update last_run. '
        '4. Deactivate one-time tasks after execution.'
    )


@shared_task
def summarise_sessions():
    """
    Celery Beat task — runs every hour.
    Finds channels with recent conversation activity and creates EpisodicMemory summaries.
    """
    raise NotImplementedError(
        '1. Find channels with ConversationLog entries in the last hour with no EpisodicMemory created. '
        '2. For each: call MemoryManager.summarise_session(). '
    )
