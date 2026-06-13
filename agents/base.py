class BaseAgent:
    """
    Base class for all agents.
    Handles memory retrieval, intent classification, pre-composition,
    budget enforcement, tool loading, LangGraph execution, and episode storage.
    Subagents only implement handle().
    """

    agent_type              = None
    memory_layers           = ['conversation']
    default_context_level   = 'standard'
    known_intents           = []

    def __init__(self, config):
        raise NotImplementedError('Load tools, memory manager, llm, budget enforcer, and build LangGraph graph.')

    def process(self, message: str, sender: str, channel_binding) -> str:
        raise NotImplementedError(
            'Full pipeline: identity → intent classification → memory retrieval '
            '→ pre-composition → budget check → handle() → store episode → return reply.'
        )

    def handle(self, message: str, context, person, intent) -> str:
        raise NotImplementedError('Override in subagents. Default runs run_graph().')

    def run_graph(self, message: str, context, person, intent) -> str:
        raise NotImplementedError('Execute LangGraph ReAct loop with loaded tools and composed context.')

    def precompose(self, message: str, memories: dict, person) -> str:
        raise NotImplementedError('Cheap nano LLM call — synthesise raw memories into tight context string.')

    def _build_graph(self):
        raise NotImplementedError('Build and return LangGraph StateGraph for this agent.')

    def _load_tools(self):
        raise NotImplementedError('Load tools from TOOL_REGISTRY based on config.enabled_tools.')
