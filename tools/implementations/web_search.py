from tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    Web search via Tavily API.
    Falls back to DuckDuckGo if Tavily credits are exhausted or unavailable.
    """

    name        = 'web_search'
    description = (
        'Search the web for current information about companies, people, industries, or news. '
        'Input: search query string. '
        'Returns list of results with title, url, and snippet.'
    )

    def _run(self, query: str) -> dict:
        raise NotImplementedError('Call Tavily API with query. Return structured results.')

    def _fallback(self, query: str) -> dict:
        raise NotImplementedError('Call DuckDuckGo search API as fallback. Return structured results.')
