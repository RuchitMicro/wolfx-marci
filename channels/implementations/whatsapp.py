from channels.base_channel import BaseChannel


class WhatsAppChannel(BaseChannel):
    """
    WhatsApp channel via wweb-mcp.
    Receives webhooks from wweb-mcp Node.js process.
    Sends replies via wweb-mcp REST API.
    Thin dispatcher only — no agent logic here.
    """

    channel_type = 'whatsapp'

    def receive(self, payload: dict) -> dict:
        raise NotImplementedError(
            'Parse wweb-mcp webhook payload. '
            'Extract: sender (phone number), message (body), channel_id (groupId), '
            'pushname, timestamp, mentionedIds, messageId.'
        )

    def send(self, channel_id: str, message: str, api_base: str, api_key: str) -> bool:
        raise NotImplementedError(
            'POST to {api_base}/groups/{channel_id}/send with Bearer auth. '
            'Return True on 200/201, False otherwise.'
        )

    def dispatch(self, payload: dict):
        raise NotImplementedError(
            '1. receive() to normalise payload. '
            '2. Lookup ChannelBinding by channel_type=whatsapp + channel_id. '
            '3. load_agent() from registry. '
            '4. agent.process(). '
            '5. send() reply. '
            'Return early if no binding found.'
        )
