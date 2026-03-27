# ─────────────────────────────────────────────────────────────────
# HireOps — Production Dockerfile
# Multi-stage build: builder (deps) → final (slim runtime)
# ─────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ───────────────────────────────────
FROM python:3.13-slim AS builder

# System libraries required for psycopg2 and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pipenv and export requirements
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
    && pipenv requirements > requirements.txt

# Install Python packages into a local directory (not site-packages)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: slim runtime ─────────────────────────────────────────
FROM python:3.13-slim AS runtime

# Only runtime system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd --gid 1001 hireops \
    && useradd  --uid 1001 --gid hireops --no-create-home hireops

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY --chown=hireops:hireops . .

# Create required directories
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R hireops:hireops /app

USER hireops

# Expose Gunicorn port
EXPOSE 8000

# Set production environment
ENV ENV=production \
    DJANGO_SETTINGS_MODULE=config.settings \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Default: run Gunicorn (override for Celery worker)
CMD ["gunicorn", "config.wsgi:application", \
     "--config", "gunicorn.conf.py"]
