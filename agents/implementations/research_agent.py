from agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Autonomous research agent.
    Researches companies, people, and industries using web and LinkedIn tools.
    Stores results in EntityMemory for future retrieval.
    Typically invoked via AgentBus by other agents, not directly by users.
    """

    agent_type              = 'research'
    memory_layers           = ['entity', 'semantic']
    default_context_level   = 'full'
    known_intents           = [
        'company_research', # context: full
        'person_lookup',    # context: full
        'industry_scan',    # context: standard
    ]

    def handle(self, message: str, context, person, intent) -> str:
        raise NotImplementedError(
            '1. Extract entity name from message. '
            '2. Check EntityMemory — return cached if fresh. '
            '3. If stale or missing: run_graph() with research tools. '
            '4. Store result in EntityMemory. '
            '5. Return formatted research summary.'
        )
