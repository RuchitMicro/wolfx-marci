"""
agents/implementations/marci_team.py

MarciTeamAgent — General team assistant for the main WOLFx WhatsApp group.

Responsibilities:
    - Answer questions about WOLFx services, team, clients, values
    - Help draft messages, emails, or content
    - Handle reminders
    - General team coordination

Restrictions:
    - Never accesses CRM
    - Never runs SQL
    - Always conversational — no data queries
    - No tools enabled by default

Extends BaseAgent — implements handle() only.
Everything else is inherited.
"""

import logging

from agents.base import BaseAgent

logger = logging.getLogger(__name__)


class MarciTeamAgent(BaseAgent):
    """
    General team assistant.
    Operates in the main WOLFx WhatsApp group.
    Pure LLM — no tools unless explicitly enabled in AgentConfig.
    """

    agent_type              = 'marci_team'
    memory_layers           = ['conversation', 'episodic']
    default_context_level   = 'minimal'
    known_intents           = [
        'wolfx_question',   # context: minimal — questions about WOLFx
        'reminder_set',     # context: none    — set a reminder
        'draft_request',    # context: minimal — draft a message or email
        'general',          # context: minimal — everything else
    ]

    def handle(
        self,
        message:        str,
        context:        str,
        sender_name:    str,
        intent:         str,
        channel_id:     str,
    ) -> str:
        """
        Routes by intent then runs the LangGraph graph.

        reminder_set    → TODO: call reminder tool directly, skip graph
                          for now falls through to run_graph() as conversational
        all others      → run_graph() with pure LLM, no tools
        """
        logger.info(f'[MarciTeamAgent] handle() — intent={intent} sender={sender_name}')

        # TODO: when reminder tool is implemented, intercept here:
        # if intent == 'reminder_set':
        #     return self._handle_reminder(message, sender_name, channel_id)

        return self.run_graph(
            message     = message,
            context     = context,
            sender_name = sender_name,
            intent      = intent,
            channel_id  = channel_id,
        )