from django.views           import View
from django.http            import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """
    Receives incoming webhooks from wweb-mcp Node.js process.
    Thin entry point only — parses payload and dispatches to WhatsAppChannel.
    No agent logic, no memory, no LLM calls here.
    """

    def post(self, request):
        raise NotImplementedError(
            '1. Parse JSON payload from request.body. '
            '2. Return 400 on invalid JSON. '
            '3. Import WhatsAppChannel from channels.implementations.whatsapp. '
            '4. Call channel.dispatch(payload) as a Celery task. '
            '5. Return {"status": "ok"} immediately — do not wait for agent response.'
        )

    def get(self, request):
        return JsonResponse({'status': 'ok', 'message': 'WhatsApp webhook endpoint is live.'})
