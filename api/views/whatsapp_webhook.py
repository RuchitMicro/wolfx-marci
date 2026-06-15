"""
api/views/whatsapp_webhook.py

Receives incoming webhooks from wweb-mcp Node.js process.
Thin entry point only — parses payload, fires Celery task, returns immediately.
No agent logic here.
"""

import json
import logging

from django.views               import View
from django.http                import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators    import method_decorator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """
    POST /api/webhook/whatsapp/
    Receives wweb-mcp webhook, dispatches to Celery, returns 200 immediately.
    """

    def post(self, request):
        # ── Parse payload ──
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning('[WhatsAppWebhookView] Invalid JSON payload')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        logger.debug(f'[WhatsAppWebhookView] Received payload: {payload}')

        # ── Fire Celery task ──
        from bus.tasks import dispatch_whatsapp_message
        dispatch_whatsapp_message.delay(payload)

        # ── Return immediately — do not wait for agent ──
        return JsonResponse({'status': 'ok'})

    def get(self, request):
        return JsonResponse({'status': 'ok', 'message': 'WhatsApp webhook endpoint is live.'})