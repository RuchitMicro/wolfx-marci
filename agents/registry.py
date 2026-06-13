from agents.implementations.marci_sales    import MarciSalesAgent
from agents.implementations.marci_team     import MarciTeamAgent
from agents.implementations.research_agent import ResearchAgent
from agents.implementations.broadcast_agent import BroadcastAgent


AGENT_REGISTRY = {
    'marci_sales':  MarciSalesAgent,
    'marci_team':   MarciTeamAgent,
    'research':     ResearchAgent,
    'broadcast':    BroadcastAgent,
}


def load_agent(agent_type: str, config):
    raise NotImplementedError(
        'Look up agent_type in AGENT_REGISTRY. '
        'Raise ValueError if not found. '
        'Instantiate and return the agent with config.'
    )
