from agents.base import BaseAgent


class MarciSalesAgent(BaseAgent):
    """
    Sales intelligence agent.
    Handles CRM queries, strategic advice, outreach drafts, and reminders.
    Operates in the WOLFx sales WhatsApp group.
    """

    agent_type              = 'marci_sales'
    memory_layers           = ['conversation', 'episodic', 'entity']
    default_context_level   = 'standard'
    known_intents           = [
        'crm_query',        # context: full
        'strategic_advice', # context: standard
        'draft_request',    # context: standard
        'reminder_set',     # context: none
        'general',          # context: minimal
    ]

    def handle(self, message: str, context, person, intent) -> str:
        raise NotImplementedError(
            'Route by intent: '
            'crm_query → run_graph() with CRM tools. '
            'strategic_advice → run_graph() with analysis tools. '
            'draft_request → run_graph() with draft_writer tool. '
            'reminder_set → call reminder tool directly, skip graph. '
            'general → run_graph() with standard tools.'
        )
