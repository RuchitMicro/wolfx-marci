"""
api/views/health.py

Health check endpoint.
Checks Django, PostgreSQL, Redis, Celery.
Returns 200 if all healthy, 503 if any critical service is down.
"""

import logging

from django.views   import View
from django.http    import JsonResponse
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