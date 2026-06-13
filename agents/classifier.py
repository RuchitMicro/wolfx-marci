class IntentClassifier:
    """
    Lightweight intent classifier — one cheap nano LLM call.
    Runs before memory retrieval to determine how much context is needed.
    """

    CONTEXT_LEVELS = ['none', 'minimal', 'standard', 'full']

    def __init__(self, llm, known_intents: list):
        self.llm            = llm
        self.known_intents  = known_intents

    def classify(self, message: str, agent_type: str):
        raise NotImplementedError(
            'Call nano LLM with message + known_intents. '
            'Return an IntentResult with intent string and context_requirement level.'
        )

    def _build_prompt(self, message: str, agent_type: str) -> str:
        raise NotImplementedError('Build classification prompt including known_intents list.')


class IntentResult:
    """Result of intent classification."""

    def __init__(self, intent: str, context_requirement: str, entities: list = None):
        self.intent                 = intent
        self.context_requirement    = context_requirement
        self.entities               = entities or []

    def __repr__(self):
        return f'IntentResult(intent={self.intent}, context={self.context_requirement})'
