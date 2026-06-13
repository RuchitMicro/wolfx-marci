from tools.base_tool import BaseTool


class LinkedInLookupTool(BaseTool):
    """
    LinkedIn profile and company page extraction via Playwright.
    Fragile by nature — built defensively with fallbacks.
    TODO: rebuild using Cerberus Playwright patterns once stable.
    """

    name        = 'linkedin_lookup'
    description = (
        'Look up a LinkedIn profile or company page and extract key information. '
        'Input: LinkedIn URL or person/company name. '
        'Returns name, title, company, summary, and recent activity.'
    )

    def _run(self, linkedin_url: str = '', name: str = '') -> dict:
        raise NotImplementedError('Playwright-based LinkedIn extraction. Handle auth, rate limits, DOM changes.')

    def _fallback(self, linkedin_url: str = '', name: str = '') -> dict:
        raise NotImplementedError('Return partial data from web_search if LinkedIn extraction fails.')
