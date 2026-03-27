"""
apps/common/health.py
─────────────────────────────────────────────────────────────────
/health/  — used by load balancers, Kubernetes liveness/readiness
probes, and uptime monitors.

Checks:
  database   — can we execute a trivial query?
  cache      — can we read/write to Redis?
  celery     — are workers responding to pings? (optional)

Returns 200 OK when everything is healthy,
        503 Service Unavailable with details when something is down.
"""
import time
import logging

from django.db import connections, OperationalError
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def _check_database() -> dict:
    t0 = time.monotonic()
    try:
        connections['default'].ensure_connection()
        connections['default'].cursor().execute('SELECT 1')
        return {'status': 'ok', 'latency_ms': round((time.monotonic() - t0) * 1000, 1)}
    except OperationalError as exc:
        logger.error('Health: database check failed', extra={'error': str(exc)})
        return {'status': 'error', 'detail': str(exc)}


def _check_cache() -> dict:
    t0 = time.monotonic()
    try:
        key = '_health_check'
        cache.set(key, 'ok', timeout=5)
        value = cache.get(key)
        if value != 'ok':
            raise RuntimeError('Cache read/write mismatch')
        cache.delete(key)
        return {'status': 'ok', 'latency_ms': round((time.monotonic() - t0) * 1000, 1)}
    except Exception as exc:
        logger.warning('Health: cache check failed', extra={'error': str(exc)})
        return {'status': 'degraded', 'detail': str(exc)}


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /health/
    Public — no auth required. Designed for load-balancer probes.
    """
    checks = {
        'database': _check_database(),
        'cache':    _check_cache(),
    }

    all_ok = all(c['status'] == 'ok' for c in checks.values())
    has_error = any(c['status'] == 'error' for c in checks.values())

    http_status = (
        status.HTTP_200_OK         if all_ok    else
        status.HTTP_503_SERVICE_UNAVAILABLE if has_error else
        status.HTTP_200_OK  # degraded (cache down) is still somewhat OK
    )

    return Response(
        {
            'status':  'ok' if all_ok else ('error' if has_error else 'degraded'),
            'checks':  checks,
            'version': '1.0.0',
        },
        status=http_status,
    )
