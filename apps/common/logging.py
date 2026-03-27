"""
apps/common/logging.py
─────────────────────────────────────────────────────────────────
Structured JSON log formatter.

Every log record is emitted as a single-line JSON object that log
aggregators (Datadog, CloudWatch, GCP Logging, ELK) can parse and
index automatically.

Fields emitted:
  timestamp  — ISO-8601 UTC
  level      — DEBUG / INFO / WARNING / ERROR / CRITICAL
  logger     — dotted logger name
  message    — the log message string
  request_id — correlates logs to a single HTTP request
  exc_info   — stringified traceback (error logs only)
  extra.*    — any extra fields passed to logger.xxx(extra={...})
"""
import json
import logging
import traceback
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': datetime.now(tz=timezone.utc).isoformat(),
            'level':     record.levelname,
            'logger':    record.name,
            'message':   record.getMessage(),
            'request_id': getattr(record, 'request_id', '-'),
        }

        # Include extra fields passed by the caller
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'message',
                'request_id',
            }:
                try:
                    json.dumps(value)   # only include JSON-serialisable values
                    log_record[key] = value
                except (TypeError, ValueError):
                    log_record[key] = str(value)

        # Append traceback for errors
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)

        return json.dumps(log_record, default=str)
