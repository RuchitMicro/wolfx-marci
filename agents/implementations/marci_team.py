from agents.base import BaseAgent


class MarciTeamAgent(BaseAgent):
    """
    General team assistant agent.
    Handles WOLFx knowledge questions, reminders, coordination.
    Never accesses CRM. Operates in the main WOLFx WhatsApp group.
    Always routes to conversational — never data_query.
    """

    agent_type              = 'marci_team'
    memory_layers           = ['conversation', 'episodic']
    default_context_level   = 'minimal'
    known_intents           = [
        'wolfx_question',   # context: minimal
        'reminder_set',     # context: none
        'draft_request',    # context: minimal
        'general',          # context: minimal
    ]

    def handle(self, message: str, context, person, intent) -> str:
        raise NotImplementedError(
            'Route by intent: '
            'wolfx_question → run_graph() with WOLFx knowledge. '
            'reminder_set → call reminder tool directly. '
            'draft_request → run_graph() with draft_writer. '
            'general → run_graph() conversationally.'
        )
