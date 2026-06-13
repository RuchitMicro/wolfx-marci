from tools.base_tool import BaseTool


class WebBrowseTool(BaseTool):
    """
    Full page extraction via Playwright.
    Used when web_search results are insufficient and full page content is needed.
    Calls the web-mcp Node.js process via REST API.
    """

    name        = 'web_browse'
    description = (
        'Open a URL and extract full page content including JavaScript-rendered content. '
        'Input: url string. '
        'Returns page title, main content text, and key metadata.'
    )

    def _run(self, url: str) -> dict:
        raise NotImplementedError('POST to web-mcp REST API with url. Return extracted page content.')

    def _fallback(self, url: str) -> dict:
        raise NotImplementedError('Simple requests + BeautifulSoup fallback if web-mcp is unreachable.')
