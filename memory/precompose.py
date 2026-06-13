class PreComposer:
    """
    Cheap LLM call (gpt-5-nano) that synthesises raw retrieved memory
    into a tight 2-3 sentence context block for the main agent call.
    Skipped entirely when context_requirement is 'none'.
    """

    def __init__(self, llm):
        self.llm = llm

    def compose(self, message: str, memories: dict, person) -> str:
        raise NotImplementedError(
            'Take raw memories dict and incoming message. '
            'Return a 2-3 sentence context summary string. '
            'Return empty string if no relevant context found.'
        )

    def _build_prompt(self, message: str, memories: dict, person) -> str:
        raise NotImplementedError('Build the pre-composition prompt from message + memories + person identity.')
