"""
apps/common/middleware.py
─────────────────────────────────────────────────────────────────
RequestIDMiddleware — attaches a unique X-Request-ID to every
HTTP request and response.

• If the upstream proxy passes X-Request-ID, we re-use it (useful
  for correlating logs across load-balancer → app → celery).
• Otherwise we generate one with uuid4.
• The ID is injected into the Python logging context so every log
  line emitted during that request carries the same ID.
"""
import uuid
import logging


class RequestIDMiddleware:
    HEADER = 'HTTP_X_REQUEST_ID'
    RESPONSE_HEADER = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(self.HEADER) or str(uuid.uuid4())
        request.request_id = request_id

        # Inject into log records for this thread
        _old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = _old_factory(*args, **kwargs)
            record.request_id = request_id
            return record

        logging.setLogRecordFactory(record_factory)

        response = self.get_response(request)

        # Restore factory & echo ID in response header
        logging.setLogRecordFactory(_old_factory)
        response[self.RESPONSE_HEADER] = request_id
        return response
