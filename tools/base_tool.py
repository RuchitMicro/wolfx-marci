class BaseTool:
    """
    Base class for all tools.
    Handles error catching, fallback chaining, and logging.
    Subclasses implement _run() and optionally _fallback().
    """

    name        = None
    description = None

    def run(self, **kwargs) -> dict:
        raise NotImplementedError(
            'Call _run(). On exception call _fallback(). '
            'If both fail raise ToolExecutionError with friendly message.'
        )

    def _run(self, **kwargs) -> dict:
        raise NotImplementedError('Core tool logic. Override in subclasses.')

    def _fallback(self, **kwargs) -> dict:
        raise NotImplementedError('Fallback logic if _run() fails. Override if fallback exists.')

    def to_langchain_tool(self):
        raise NotImplementedError('Return a LangChain StructuredTool wrapping this tool.')


class ToolExecutionError(Exception):
    """Raised when a tool and all its fallbacks fail."""
    pass
