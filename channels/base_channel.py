class BaseChannel:
    """
    Interface for all channel implementations.
    A channel receives messages from the outside world and sends replies.
    It knows nothing about agents, memory, or tools.
    """

    channel_type = None

    def receive(self, payload: dict) -> dict:
        raise NotImplementedError(
            'Parse raw incoming payload into a normalised dict: '
            '{sender, message, channel_id, pushname, timestamp, raw}'
        )

    def send(self, channel_id: str, message: str, api_base: str, api_key: str) -> bool:
        raise NotImplementedError('Send message to channel. Return True on success, False on failure.')

    def dispatch(self, payload: dict):
        raise NotImplementedError(
            'Full receive → lookup binding → load agent → process → send pipeline. '
            'Called by the webhook view.'
        )
