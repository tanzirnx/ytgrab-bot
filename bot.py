"""
═══════════════════════════════════════════════════════════
  YTGrab Bot - Main Entry Point (Phase 2)
  Telegram Bot: @YTGrabDownBot
  YouTube/Media Downloader using yt-dlp
  Version: 1.0.0 | Phase 2
  License: Free & Open Source
═══════════════════════════════════════════════════════════
"""

import sys
import time
import asyncio
from pathlib import Path

from telegram import Update, BotCommand, BotCommandScopeDefault
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from loguru import logger

from config import Config
from models.database import db
from services.file_manager import file_manager
from utils.helpers import Helpers

# Phase 1 Handlers
from handlers.start_handler import (
    start_command, help_command, faq_command,
    settings_command, ping_command, version_command,
    callback_handler,
)
from handlers.download_handler import (
    url_handler, mp3_command, mp4_command,
    info_command, best_command, search_command,
)

# Phase 2 Handlers
from handlers.playlist_handler import (
    playlist_command, plinfo_command, plrange_command,
    playlist_callback_handler,
)
from handlers.audio_handler import (
    m4a_command, flac_command, ogg_command,
    wav_command, opus_command, aac_command,
)
from handlers.video_handler import (
    webm_command, mkv_command, worst_command,
    gif_command, clip_command, noaudio_command,
)
from handlers.admin_handler import (
    admin_command, stats_command, broadcast_command,
    ban_command, unban_command, setlimit_command,
    maintenance_command, logs_command, update_command,
    restart_command, admin_callback_handler,
)
from handlers.settings_handler import (
    setquality_command, setformat_command, setlang_command,
    setthumb_command, setsubs_command, setnotify_command,
    setfilename_command, reset_command, mydefaults_command,
)
from handlers.utility_handler import (
    queue_command, cancel_command, clearqueue_command,
    trending_command, shorts_command, batch_command,
    report_command, feedback_command, suggest_command,
)


# ─── Logging Setup ──────────────────────────────────────────

def setup_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        Config.LOG_FILE,
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )


# ─── Bot Commands Setup ─────────────────────────────────────

async def setup_commands(app: Application):
    commands = [
        BotCommand("start", "🏠 Start & Welcome"),
        BotCommand("help", "📖 Help & All Commands"),
        BotCommand("mp3", "🎵 Download Audio (MP3)"),
        BotCommand("mp4", "🎬 Download Video (MP4)"),
        BotCommand("best", "✨ Best Quality Download"),
        BotCommand("info", "📋 Get Video Info"),
        BotCommand("search", "🔍 Search YouTube"),
        BotCommand("pl", "📁 Download Playlist"),
        BotCommand("trending", "🔥 Trending Videos"),
        BotCommand("settings", "⚙️ Bot Settings"),
        BotCommand("mydefaults", "📄 View My Settings"),
        BotCommand("queue", "📊 Download Queue"),
        BotCommand("faq", "❓ FAQ"),
        BotCommand("ping", "🏓 Bot Speed"),
        BotCommand("version", "🤖 Bot Version"),
        BotCommand("report", "🐛 Report a Bug"),
        BotCommand("feedback", "💬 Send Feedback"),
    ]
    await app.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("✅ Bot commands registered (17 commands)")


# ─── Maintenance Check Middleware ───────────────────────────

async def maintenance_check(update: Update, context) -> bool:
    """Check if bot is in maintenance mode."""
    if Config.MAINTENANCE_MODE:
        if update.effective_user and update.effective_user.id != Config.ADMIN_ID:
            if update.message:
                await update.message.reply_text(
                    "🔧 <b>Under Maintenance</b>\n\n"
                    "The bot is currently under maintenance.\n"
                    "Please try again in a few minutes. 🙏",
                    parse_mode="HTML",
                )
            return True
    return False


# ─── Error Handler ──────────────────────────────────────────

async def error_handler(update: object, context):
    logger.error(f"❌ Unhandled error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ <b>Oops! Something went wrong.</b>\n\n"
                "The error has been logged. Please try again.\n"
                "Use /report to notify the admin.",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ─── Scheduled Tasks ────────────────────────────────────────

async def scheduled_cleanup(app: Application):
    """Periodic temp file cleanup."""
    cleaned = await file_manager.scheduled_cleanup()
    if cleaned > 0:
        logger.info(f"🧹 Scheduled cleanup: {cleaned} files removed")


# ─── Post-Init ──────────────────────────────────────────────

async def post_init(app: Application):
    await setup_commands(app)
    app.bot_data["start_time"] = time.time()

    # Schedule periodic cleanup
    app.job_queue.run_repeating(
        scheduled_cleanup,
        interval=Config.CLEANUP_INTERVAL_MIN * 60,
        first=60,
        name="cleanup",
    )

    logger.info(f"🤖 Bot @{Config.BOT_USERNAME} is running! (Phase 2)")
    logger.info(f"👤 Admin ID: {Config.ADMIN_ID}")
    logger.info(f"📊 Max concurrent downloads: {Config.MAX_CONCURRENT_DOWNLOADS}")
    logger.info(f"📋 Max queue size: {Config.MAX_QUEUE_SIZE}")


# ─── Main ───────────────────────────────────────────────────

def main():
    setup_logging()
    Config.validate()

    logger.info("═══════════════════════════════════════════════")
    logger.info("  🚀 Starting YTGrab Bot v1.0.0 (Phase 2)")
    logger.info(f"  📱 @{Config.BOT_USERNAME}")
    logger.info(f"  📊 Features: 70+ commands | 1000+ platforms")
    logger.info("═══════════════════════════════════════════════")

    asyncio.get_event_loop().run_until_complete(db.initialize())

    app = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ═══════════════════════════════════════════════════════
    # REGISTER ALL HANDLERS
    # ═══════════════════════════════════════════════════════

    # ─── Phase 1: Core Commands ─────────────────────────────
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("faq", faq_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("version", version_command))
    app.add_handler(CommandHandler(["mp3", "audio"], mp3_command))
    app.add_handler(CommandHandler(["mp4", "video"], mp4_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("best", best_command))
    app.add_handler(CommandHandler("search", search_command))

    # ─── Phase 2: Audio Commands ────────────────────────────
    app.add_handler(CommandHandler("m4a", m4a_command))
    app.add_handler(CommandHandler("flac", flac_command))
    app.add_handler(CommandHandler("ogg", ogg_command))
    app.add_handler(CommandHandler("wav", wav_command))
    app.add_handler(CommandHandler("opus", opus_command))
    app.add_handler(CommandHandler("aac", aac_command))

    # ─── Phase 2: Video Commands ────────────────────────────
    app.add_handler(CommandHandler("webm", webm_command))
    app.add_handler(CommandHandler("mkv", mkv_command))
    app.add_handler(CommandHandler("worst", worst_command))
    app.add_handler(CommandHandler("gif", gif_command))
    app.add_handler(CommandHandler("clip", clip_command))
    app.add_handler(CommandHandler("noaudio", noaudio_command))

    # ─── Phase 2: Playlist Commands ─────────────────────────
    app.add_handler(CommandHandler(["pl", "playlist"], playlist_command))
    app.add_handler(CommandHandler("plinfo", plinfo_command))
    app.add_handler(CommandHandler("plrange", plrange_command))

    # ─── Phase 2: Settings Commands ─────────────────────────
    app.add_handler(CommandHandler("setquality", setquality_command))
    app.add_handler(CommandHandler("setformat", setformat_command))
    app.add_handler(CommandHandler("setlang", setlang_command))
    app.add_handler(CommandHandler("setthumb", setthumb_command))
    app.add_handler(CommandHandler("setsubs", setsubs_command))
    app.add_handler(CommandHandler("setnotify", setnotify_command))
    app.add_handler(CommandHandler("setfilename", setfilename_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("mydefaults", mydefaults_command))

    # ─── Phase 2: Utility Commands ──────────────────────────
    app.add_handler(CommandHandler("queue", queue_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("clearqueue", clearqueue_command))
    app.add_handler(CommandHandler("trending", trending_command))
    app.add_handler(CommandHandler("shorts", shorts_command))
    app.add_handler(CommandHandler("batch", batch_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    app.add_handler(CommandHandler("suggest", suggest_command))

    # ─── Phase 2: Admin Commands ────────────────────────────
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("setlimit", setlimit_command))
    app.add_handler(CommandHandler("maintenance", maintenance_command))
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("restart", restart_command))

    # ─── Callback Query Handler (ALL inline buttons) ────────
    app.add_handler(CallbackQueryHandler(callback_handler))

    # ─── URL Auto-Detection (LAST - catches all text) ───────
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(r'https?://'),
            url_handler,
        )
    )

    # ─── Error Handler ──────────────────────────────────────
    app.add_error_handler(error_handler)

    # ─── Start Polling ──────────────────────────────────────
    logger.info("🟢 Bot is now polling for updates...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
