# ═══════════════════════════════════════════════════════════
# YTGrab Bot - Docker Image
# Bot: @YTGrabDownBot
# Multi-stage build for minimal image size
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user (security)
RUN useradd -m -r ytgrab

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=ytgrab:ytgrab . .

# Create necessary directories
RUN mkdir -p /tmp/ytgrab/downloads /tmp/ytgrab/processing /app/logs /app/data && \
    chown -R ytgrab:ytgrab /tmp/ytgrab /app/logs /app/data

# Switch to non-root user
USER ytgrab

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f https://api.telegram.org/bot${BOT_TOKEN}/getMe || exit 1

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TEMP_DIR=/tmp/ytgrab

# Run bot
CMD ["python", "bot.py"]
