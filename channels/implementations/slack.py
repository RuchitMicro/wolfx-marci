from channels.base_channel import BaseChannel


class SlackChannel(BaseChannel):
    """
    Slack channel — future implementation.
    """

    channel_type = 'slack'

    def receive(self, payload: dict) -> dict:
        raise NotImplementedError('Parse Slack event payload.')

    def send(self, channel_id: str, message: str, api_base: str, api_key: str) -> bool:
        raise NotImplementedError('Send message via Slack API.')

    def dispatch(self, payload: dict):
        raise NotImplementedError('Full Slack dispatch pipeline.')
