from agents.base import BaseAgent


class BroadcastAgent(BaseAgent):
    """
    Proactive broadcast agent.
    Generates and posts scheduled content to community groups.
    Does not respond to user messages — only fires from ScheduledTask.
    Supports optional human approval before posting.
    """

    agent_type              = 'broadcast'
    memory_layers           = []
    default_context_level   = 'none'
    known_intents           = [
        'scheduled_post',   # context: none
        'signal_alert',     # context: minimal
    ]

    def handle(self, message: str, context, person, intent) -> str:
        raise NotImplementedError(
            '1. Generate content using web_search + draft_writer tools. '
            '2. If requires_approval: send preview to admin channel and wait. '
            '3. If approved or no approval needed: post to target channel. '
            '4. Return confirmation string.'
        )
