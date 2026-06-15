"""
agents/registry.py

Agent registry — maps agent_type strings to Python classes.
Adding a new agent = one file + one line here + one AgentConfig in admin.
"""

import logging

logger = logging.getLogger(__name__)


def _build_registry() -> dict:
    """
    Lazy imports to avoid circular imports and Django app loading issues.
    Called once on first registry access.
    """
    from agents.implementations.marci_team     import MarciTeamAgent
    from agents.implementations.marci_sales    import MarciSalesAgent
    from agents.implementations.research_agent import ResearchAgent
    from agents.implementations.broadcast_agent import BroadcastAgent

    return {
        'marci_team':   MarciTeamAgent,
        'marci_sales':  MarciSalesAgent,
        'research':     ResearchAgent,
        'broadcast':    BroadcastAgent,
    }


_registry = None


def get_registry() -> dict:
    """Returns the agent registry, building it on first call."""
    global _registry
    if _registry is None:
        _registry = _build_registry()
    return _registry


def load_agent(agent_type: str, config):
    """
    Loads and instantiates an agent by agent_type.
    Raises ValueError if agent_type is not in registry.

    Args:
        agent_type: string identifier e.g. 'marci_team'
        config: AgentConfig Django model instance

    Returns:
        Instantiated agent ready to call process()
    """
    registry = get_registry()

    cls = registry.get(agent_type)
    if not cls:
        available = list(registry.keys())
        raise ValueError(
            f'Unknown agent_type: "{agent_type}". '
            f'Available agents: {available}'
        )

    logger.info(f'[registry] Loading agent: {agent_type}')
    return cls(config)