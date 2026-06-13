from tools.base_tool import BaseTool


class CompanyResearchTool(BaseTool):
    """
    Compound tool — web_search + web_browse + LLM summarise.
    Researches a company and returns a structured profile.
    Stores result in EntityMemory after completion.
    """

    name        = 'company_research'
    description = (
        'Research a company and return a structured profile: '
        'founding, size, product, recent news, key people, and relevance to WOLFx services. '
        'Input: company name and optional website URL. '
        'Returns structured company profile dict.'
    )

    def _run(self, company_name: str, website_url: str = '') -> dict:
        raise NotImplementedError(
            '1. web_search for company name. '
            '2. web_browse company website if URL provided. '
            '3. LLM summarise into structured profile. '
            '4. Store in EntityMemory scope=global. '
            '5. Return profile dict.'
        )
