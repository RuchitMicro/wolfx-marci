"""
channels/implementations/whatsapp.py

WhatsApp channel dispatcher.
Thin layer only — receive, dispatch, send.
No agent logic, no memory, no LLM calls here.
"""

import logging
import requests

from pathlib        import Path
from django.conf    import settings

from channels.base_channel import BaseChannel

logger = logging.getLogger(__name__)


class WhatsAppChannel(BaseChannel):
    """
    WhatsApp channel via wweb-mcp Node.js process.
    Receives webhooks, dispatches to agent, sends replies.
    """

    channel_type = 'whatsapp'

    def receive(self, payload: dict) -> dict:
        """
        Parses raw wweb-mcp webhook payload into a normalised dict.
        Returns None if payload is missing required fields.
        """
        sender      = payload.get('sender',     '')
        message     = payload.get('message',    '').strip()
        channel_id  = payload.get('groupId',    '')
        is_group    = payload.get('isGroup',    False)
        pushname    = payload.get('pushname',   '')
        mentions    = payload.get('mentions',   [])

        if not sender or not message or not channel_id:
            logger.warning(f'[WhatsAppChannel] Incomplete payload — skipping: {payload}')
            return None

        if not is_group:
            logger.debug(f'[WhatsAppChannel] Non-group message — ignoring')
            return None

        return {
            'sender':       sender,
            'message':      message,
            'channel_id':   channel_id,
            'pushname':     pushname,
            'mentions':     mentions,
            'raw':          payload,
        }

    def send(self, channel_id: str, message: str, api_base: str, api_key: str) -> bool:
        """
        Sends a message to a WhatsApp group via wweb-mcp REST API.
        Returns True on success, False on failure.
        """
        if not api_key:
            logger.error('[WhatsAppChannel] No API key found — cannot send message')
            return False

        try:
            response = requests.post(
                f'{api_base}/groups/{channel_id}/send',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type':  'application/json',
                },
                json    = {'message': message},
                timeout = 10,
            )
            if response.status_code in (200, 201):
                logger.info(f'[WhatsAppChannel] Message sent to {channel_id}')
                return True
            else:
                logger.error(f'[WhatsAppChannel] Send failed: {response.status_code} {response.text}')
                return False
        except Exception as exc:
            logger.error(f'[WhatsAppChannel] Send exception: {exc}')
            return False

    def dispatch(self, payload: dict):
        """
        Full pipeline:
        1. receive() — normalise payload
        2. Guard checks — bot mention, authorised sender
        3. Lookup ChannelBinding
        4. load_agent() from registry
        5. agent.process()
        6. send() reply
        """
        from config.models          import ChannelBinding
        from agents.registry        import load_agent

        # ── Step 1: Normalise ──
        normalised = self.receive(payload)
        if not normalised:
            return

        sender      = normalised['sender']
        message     = normalised['message']
        channel_id  = normalised['channel_id']
        pushname    = normalised['pushname']

        # ── Step 2: Lookup ChannelBinding ──
        binding = ChannelBinding.objects.filter(
            channel_type    = 'whatsapp',
            channel_id      = channel_id,
            is_active       = True,
        ).select_related('agent').first()

        if not binding:
            logger.debug(f'[WhatsAppChannel] No active binding for group: {channel_id}')
            return

        # ── Step 3: Guard — bot mention ──
        bot_number = binding.bot_number.split('@')[0]
        if bot_number and f'@{bot_number}' not in message:
            logger.debug(f'[WhatsAppChannel] Bot not mentioned — ignoring')
            return

        # ── Step 4: Guard — authorised sender ──
        sender_clean = sender.strip().split('@')[0]
        cfg = binding.agent
        if cfg.authorised_numbers and cfg.authorised_numbers.strip():
            allowed = [n.strip().split('@')[0] for n in cfg.authorised_numbers.split(',') if n.strip()]
            if sender_clean not in allowed:
                logger.warning(f'[WhatsAppChannel] Unauthorised sender: {sender}')
                return

        # ── Step 5: Load agent ──
        try:
            agent = load_agent(cfg.agent_type, cfg)
        except Exception as exc:
            logger.error(f'[WhatsAppChannel] Failed to load agent {cfg.agent_type}: {exc}')
            return

        # ── Step 6: Process ──
        try:
            reply = agent.process(
                message         = message,
                sender          = sender,
                channel_binding = binding,
            )
        except Exception as exc:
            logger.exception(f'[WhatsAppChannel] Agent process error: {exc}')
            reply = 'Something went wrong on my end. Please try again.'

        # ── Step 7: Send reply ──
        self.send(
            channel_id  =   channel_id,
            message     =   reply,
            api_base    =   binding.api_base,
            api_key     =   binding.api_key,
        )

    