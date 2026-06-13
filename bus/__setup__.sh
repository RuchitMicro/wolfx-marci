#!/bin/bash
set -euo pipefail

APP="bus"

rm -f $APP/models.py $APP/views.py

# ── agent_bus.py ──
cat > $APP/agent_bus.py << 'EOF'
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
EOF

# ── tasks.py ──
cat > $APP/tasks.py << 'EOF'
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
EOF

# ── apps.py ──
cat > $APP/apps.py << 'EOF'
from django.apps import AppConfig


class BusConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'bus'
    verbose_name        = 'Agent Bus'
EOF

# ── admin.py ──
cat > $APP/admin.py << 'EOF'
from django.contrib import admin

# No models in bus app — AgentTask lives in config app.
# Register bus-related admin views here if needed in future.
EOF

echo ""
echo "bus app structure created successfully."