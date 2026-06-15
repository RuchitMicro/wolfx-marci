"""
tools/registry.py

Tool registry — maps tool name strings to Python classes.
Adding a new tool = one file + one line here.
Agents only see tools in their enabled_tools list.
"""

import logging

logger = logging.getLogger(__name__)


def _build_registry() -> dict:
    """
    Lazy imports to avoid circular imports on startup.
    """
    from tools.implementations.crm_query        import CRMQueryTool
    from tools.implementations.web_search       import WebSearchTool
    from tools.implementations.web_browse       import WebBrowseTool
    from tools.implementations.draft_writer     import DraftWriterTool
    from tools.implementations.company_research import CompanyResearchTool
    from tools.implementations.linkedin_lookup  import LinkedInLookupTool
    from tools.implementations.reminder         import ReminderTool

    return {
        'crm_query':          CRMQueryTool,
        'web_search':         WebSearchTool,
        'web_browse':         WebBrowseTool,
        'draft_writer':       DraftWriterTool,
        'company_research':   CompanyResearchTool,
        'linkedin_lookup':    LinkedInLookupTool,
        'reminder':           ReminderTool,
    }


_registry = None


def get_registry() -> dict:
    global _registry
    if _registry is None:
        _registry = _build_registry()
    return _registry


def get_tools_for_agent(enabled_tools: list) -> list:
    """
    Instantiates and returns tool instances for each name in enabled_tools.
    Skips unknown tool names with a warning.
    Returns empty list if enabled_tools is empty — agent runs in pure LLM mode.

    Args:
        enabled_tools: list of tool name strings from AgentConfig.enabled_tools

    Returns:
        List of instantiated tool objects ready to use.
    """
    if not enabled_tools:
        return []

    registry    = get_registry()
    tools       = []

    for name in enabled_tools:
        cls = registry.get(name)
        if cls:
            tools.append(cls())
            logger.info(f'[tool_registry] Loaded tool: {name}')
        else:
            logger.warning(f'[tool_registry] Unknown tool: "{name}" — skipping')

    return tools