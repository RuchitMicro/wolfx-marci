from tools.base_tool import BaseTool


class CRMQueryTool(BaseTool):
    """
    Calls wolfx-networking MCP read-only API to fetch CRM data.
    Never accesses the database directly.
    Falls back to a friendly error message if the API is unreachable.
    """

    name        = 'crm_query'
    description = (
        'Query the WOLFx CRM database for outreach records, rep performance, '
        'pipeline stages, reply rates, and follow-up data. '
        'Input: a natural language question about CRM data. '
        'Returns structured data as a dict.'
    )

    def _run(self, query: str) -> dict:
        raise NotImplementedError(
            'POST to wolfx-networking MCP API endpoint with query. '
            'Parse and return structured response.'
        )

    def _fallback(self, query: str) -> dict:
        raise NotImplementedError('Return friendly error dict if CRM API is unreachable.')
