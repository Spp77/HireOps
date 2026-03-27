"""
gunicorn.conf.py
─────────────────────────────────────────────────────────────────
Gunicorn WSGI server configuration.

Tuning guide:
  workers  = (2 × CPU_count) + 1     — CPU-bound Django processes
  threads  = 2-4 per worker          — handles I/O-bound requests
  timeout  = 30s                      — kill stuck requests
  keepalive = 5s                      — reuse connections (behind nginx/ALB)

For horizontal scaling:
  - Run multiple containers/VMs each with this config
  - Place a load balancer (nginx / AWS ALB) in front
  - Redis ensures shared state (cache, sessions, rate-limit counters)
"""
import multiprocessing
import os

# ── Worker processes ──────────────────────────────────────────────
# Default: (2 × cores) + 1, capped at 9 to avoid memory pressure.
# Tune with GUNICORN_WORKERS env var in production.
workers = int(os.environ.get('GUNICORN_WORKERS', min((2 * multiprocessing.cpu_count()) + 1, 9)))
worker_class = 'sync'       # Use 'gthread' if you want threading
threads      = int(os.environ.get('GUNICORN_THREADS', 2))

# ── Bind ─────────────────────────────────────────────────────────
bind = '0.0.0.0:8000'

# ── Timeouts ─────────────────────────────────────────────────────
timeout       = 30          # Kill workers stuck > 30s
keepalive     = 5           # Reuse TCP connections for 5s (behind ALB)
graceful_timeout = 30       # Graceful shutdown window

# ── Request limits ────────────────────────────────────────────────
max_requests             = 1000   # Recycle worker after N requests (guards memory leaks)
max_requests_jitter      = 100    # Random jitter prevents all workers recycling at once
worker_connections       = 1000   # Max simultaneous clients per worker

# ── Logging ──────────────────────────────────────────────────────
loglevel        = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
accesslog       = '-'   # stdout
errorlog        = '-'   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)sµs'

# ── Process naming ────────────────────────────────────────────────
proc_name = 'hireops'

# ── Security ─────────────────────────────────────────────────────
limit_request_line        = 8190    # Reject huge URLs
limit_request_fields      = 100
limit_request_field_size  = 8190
forwarded_allow_ips       = '*'     # Trust X-Forwarded-For from any proxy (set to ALB IP in prod)

# ── Hooks ─────────────────────────────────────────────────────────
def on_starting(server):
    server.log.info('HireOps Gunicorn starting with %d workers', workers)

def worker_exit(server, worker):
    server.log.info('Worker exited (pid: %s)', worker.pid)
