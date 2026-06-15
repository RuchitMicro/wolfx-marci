"""
api/views/health.py

Health check endpoint.
Checks Django, PostgreSQL, Redis, Celery.
Returns 200 if all healthy, 503 if any critical service is down.
"""

import logging
import requests

from django.views   import View
from django.http    import JsonResponse, HttpResponse
from django.utils   import timezone

logger = logging.getLogger(__name__)


class HealthView(View):
    """
    GET /api/health/
    Returns service health status for monitoring and frp tunnel verification.
    """

    def get(self, request):
        services    = {}
        healthy     = True

        # ── PostgreSQL ──
        try:
            from django.db import connection
            connection.ensure_connection()
            services['postgresql'] = 'ok'
        except Exception as exc:
            services['postgresql'] = f'error: {str(exc)}'
            healthy = False

        # ── Redis ──
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', timeout=5)
            val = cache.get('health_check')
            services['redis'] = 'ok' if val == 'ok' else 'error: unexpected value'
            if val != 'ok':
                healthy = False
        except Exception as exc:
            services['redis'] = f'error: {str(exc)}'
            healthy = False

        # ── Celery ──
        try:
            from wolfx_marci.celery import app
            inspect = app.control.inspect(timeout=2)
            active  = inspect.active()
            services['celery'] = 'ok' if active else 'no workers'
            if not active:
                healthy = False
        except Exception as exc:
            services['celery'] = f'error: {str(exc)}'
            healthy = False

        status_code = 200 if healthy else 503

        return JsonResponse({
            'status':       'healthy' if healthy else 'degraded',
            'timestamp':    timezone.now().isoformat(),
            'services':     services,
        }, status=status_code)
    
class WhatsAppQRView(View):
    """
    GET /api/qr/
    Renders WhatsApp QR code for scanning.
    Fetches from wweb-mcp nginx endpoint and renders as scannable QR.
    """

    def get(self, request):
        import qrcode
        import qrcode.image.svg
        from io import BytesIO
        from xml.etree import ElementTree as ET

        try:
            response = requests.get('http://127.0.0.1:3031/qr.json', timeout=3)
            qr_string = response.json().get('qr', '')
        except Exception:
            return HttpResponse('QR not available — wweb-mcp may still be loading.', status=503)

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_string)
        qr.make(fit=True)
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        buffer = BytesIO()
        img.save(buffer)
        svg_bytes = buffer.getvalue()

        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        root = ET.fromstring(svg_bytes)
        root.set('width', '300')
        root.set('height', '300')
        svg = ET.tostring(root, encoding='unicode')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Marci — WhatsApp QR</title>
            <meta http-equiv="refresh" content="15">
            <style>
                body {{ font-family: sans-serif; display: flex; flex-direction: column;
                        align-items: center; justify-content: center; height: 100vh;
                        background: #111; color: #000; margin: 0; }}
                h2 {{ margin-bottom: 10px; }}
                p {{ color: #aaa; font-size: 13px; }}
            </style>
        </head>
        <body>
            <h2>Scan with WhatsApp</h2>
            {svg}
            <p>Auto-refreshes every 15 seconds</p>
        </body>
        </html>
        """
        return HttpResponse(html)