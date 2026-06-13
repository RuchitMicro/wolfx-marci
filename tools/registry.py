from tools.implementations.crm_query        import CRMQueryTool
from tools.implementations.web_search       import WebSearchTool
from tools.implementations.web_browse       import WebBrowseTool
from tools.implementations.draft_writer     import DraftWriterTool
from tools.implementations.company_research import CompanyResearchTool
from tools.implementations.linkedin_lookup  import LinkedInLookupTool
from tools.implementations.reminder         import ReminderTool


TOOL_REGISTRY = {
    'crm_query':          CRMQueryTool,
    'web_search':         WebSearchTool,
    'web_browse':         WebBrowseTool,
    'draft_writer':       DraftWriterTool,
    'company_research':   CompanyResearchTool,
    'linkedin_lookup':    LinkedInLookupTool,
    'reminder':           ReminderTool,
}


def get_tools_for_agent(enabled_tools: list) -> list:
    raise NotImplementedError(
        'Instantiate and return tool instances for each name in enabled_tools. '
        'Skip unknown tool names with a warning log.'
    )
