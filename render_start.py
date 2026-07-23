"""
═══════════════════════════════════════════════════════════
  YTGrab Bot - Render.com Start Script
  Runs Telegram Bot + Health Check Server
  Bot: @YTGrabDownBot
═══════════════════════════════════════════════════════════
"""

import os
import sys
import threading
import time
import logging
from pathlib import Path

# ─── Setup Directories ──────────────────────────────────────
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/ytgrab"))
(TEMP_DIR / "downloads").mkdir(parents=True, exist_ok=True)
(TEMP_DIR / "processing").mkdir(parents=True, exist_ok=True)

# ─── Health Check Server (Flask) ────────────────────────────
# Render needs an HTTP endpoint to keep the service alive

def run_health_server():
    """Run a minimal Flask server for health checks."""
    from flask import Flask, jsonify

    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Suppress Flask logs

    start_time = time.time()

    @app.route('/')
    def index():
        return jsonify({
            "status": "running",
            "bot": "@YTGrabDownBot",
            "version": "1.0.0",
        })

    @app.route('/health')
    def health():
        uptime = time.time() - start_time
        return jsonify({
            "status": "healthy",
            "uptime_seconds": round(uptime),
            "uptime_human": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m",
        })

    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)


# ─── Telegram Bot ───────────────────────────────────────────

def run_bot():
    """Run the Telegram bot (main application)."""
    # Import and run the bot
    from bot import main
    main()


# ─── Main ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("═══════════════════════════════════════════════")
    print("  🚀 YTGrab Bot - Render.com Deployment")
    print("  📱 @YTGrabDownBot")
    print("═══════════════════════════════════════════════")

    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    print("✅ Health check server started on port", os.getenv("PORT", 10000))

    # Small delay to ensure health server is up
    time.sleep(2)

    # Run bot in main thread
    print("🤖 Starting Telegram Bot...")
    try:
        run_bot()
    except KeyboardInterrupt:
        print("👋 Bot stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)
