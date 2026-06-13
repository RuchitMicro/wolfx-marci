from tools.base_tool import BaseTool


class DraftWriterTool(BaseTool):
    """
    LLM-based outreach message draft generator.
    Uses company research and rep context to write personalised messages.
    No external API calls — pure LLM generation.
    """

    name        = 'draft_writer'
    description = (
        'Write a personalised outreach message for a specific prospect. '
        'Input: prospect name, company, research notes, rep name, message stage. '
        'Returns a ready-to-send WhatsApp or LinkedIn message draft.'
    )

    def _run(self, prospect_name: str, company: str, research: str, rep_name: str, stage: str) -> dict:
        raise NotImplementedError('Call LLM with prospect context and playbook rules. Return drafted message.')
