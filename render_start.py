"""
YTGrab Bot - Render.com Start Script
Runs Telegram Bot + Health Check Server
"""

import os
import sys
import threading
import time
from pathlib import Path

TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/ytgrab"))
(TEMP_DIR / "downloads").mkdir(parents=True, exist_ok=True)
(TEMP_DIR / "processing").mkdir(parents=True, exist_ok=True)


def run_health_server():
    from flask import Flask, jsonify

    app = Flask(__name__)

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

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
        })

    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)


def run_bot():
    from bot import main
    main()


if __name__ == "__main__":
    print("=" * 45)
    print("  YTGrab Bot - Render.com")
    print("  @YTGrabDownBot")
    print("=" * 45)

    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    print("Health check server started on port", os.getenv("PORT", 10000))

    time.sleep(2)

    print("Starting Telegram Bot...")
    try:
        run_bot()
    except KeyboardInterrupt:
        print("Bot stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Bot crashed: {e}")
        sys.exit(1)
