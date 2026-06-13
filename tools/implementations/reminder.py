from tools.base_tool import BaseTool


class ReminderTool(BaseTool):
    """
    Creates ScheduledTask records for time-based reminders.
    Does not make external API calls — pure DB write.
    Uses nano LLM call to parse natural language time expressions.
    """

    name        = 'reminder'
    description = (
        'Set a reminder that fires at a specified time in a WhatsApp group. '
        'Input: reminder text and time expression (e.g. "at 5pm", "in 2 hours", "tomorrow morning"). '
        'Returns confirmation with parsed datetime.'
    )

    def _run(self, reminder_text: str, time_expression: str, channel_binding_id: int, created_by: str) -> dict:
        raise NotImplementedError(
            '1. Call nano LLM to parse time_expression into datetime. '
            '2. Create ScheduledTask record with trigger_type=time. '
            '3. Return confirmation dict with parsed trigger_at.'
        )
