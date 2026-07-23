# ═══════════════════════════════════════════════════════════
# YTGrab Bot - Render.com Dockerfile
# Includes health check server for keep-alive
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim

# Install FFmpeg & system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask

# Copy application
COPY . .

# Create temp directories
RUN mkdir -p /tmp/ytgrab/downloads /tmp/ytgrab/processing

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TEMP_DIR=/tmp/ytgrab \
    DB_PATH=/tmp/ytgrab/ytgrab.db \
    LOG_FILE=/tmp/ytgrab/bot.log

# Expose port for health check (Render requires this for Web Service)
EXPOSE 10000

# Start script
CMD ["python", "render_start.py"]
