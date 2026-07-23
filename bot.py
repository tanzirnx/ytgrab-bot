"""
═══════════════════════════════════════════════════════════
  YTGrab Bot - Main Entry Point
  Telegram Bot: @YTGrabDownBot
  YouTube/Media Downloader using yt-dlp
  Version: 1.0.0
  License: Free & Open Source
═══════════════════════════════════════════════════════════
"""

import sys
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
from handlers.start_handler import (
    start_command,
    help_command,
    faq_command,
    settings_command,
    ping_command,
    version_command,
    callback_handler,
)
from handlers.download_handler import (
    url_handler,
    mp3_command,
    mp4_command,
    info_command,
    best_command,
    search_command,
)


# ─── Logging Setup ──────────────────────────────────────────

def setup_logging():
    """Configure loguru logging."""
    logger.remove()  # Remove default handler

    # Console output
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

    # File output
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
    """Set bot commands for Telegram menu."""
    commands = [
        BotCommand("start", "🏠 Start & Welcome"),
        BotCommand("help", "📖 Help & Commands"),
        BotCommand("mp3", "🎵 Download Audio (MP3)"),
        BotCommand("mp4", "🎬 Download Video (MP4)"),
        BotCommand("best", "✨ Download Best Quality"),
        BotCommand("info", "📋 Get Video Info"),
        BotCommand("search", "🔍 Search YouTube"),
        BotCommand("settings", "⚙️ Bot Settings"),
        BotCommand("faq", "❓ FAQ"),
        BotCommand("ping", "🏓 Check Bot Speed"),
        BotCommand("version", "🤖 Bot Version"),
    ]
    await app.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("✅ Bot commands registered")


# ─── Error Handler ──────────────────────────────────────────

async def error_handler(update: object, context):
    """Handle unexpected errors."""
    logger.error(f"❌ Unhandled error: {context.error}", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ <b>Oops! Something went wrong.</b>\n\n"
                "The error has been logged. Please try again.\n"
                "If the problem persists, use /report to notify the admin.",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ─── Post-Init ──────────────────────────────────────────────

async def post_init(app: Application):
    """Actions after bot initialization."""
    await setup_commands(app)
    logger.info(f"🤖 Bot @{Config.BOT_USERNAME} is running!")
    logger.info(f"👤 Admin ID: {Config.ADMIN_ID}")


# ─── Main ───────────────────────────────────────────────────

def main():
    """Main entry point."""
    # Setup
    setup_logging()
    Config.validate()

    logger.info("═══════════════════════════════════════════")
    logger.info("  🚀 Starting YTGrab Bot v1.0.0")
    logger.info(f"  📱 @{Config.BOT_USERNAME}")
    logger.info("═══════════════════════════════════════════")

    # Initialize database
    asyncio.get_event_loop().run_until_complete(db.initialize())

    # Build application
    app = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ─── Register Handlers ──────────────────────────────────

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("faq", faq_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("version", version_command))

    # Download commands
    app.add_handler(CommandHandler(["mp3", "audio"], mp3_command))
    app.add_handler(CommandHandler(["mp4", "video"], mp4_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("best", best_command))
    app.add_handler(CommandHandler("search", search_command))

    # Callback query handler (inline buttons)
    app.add_handler(CallbackQueryHandler(callback_handler))

    # URL auto-detection (must be LAST - catches all text messages)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(r'https?://'),
            url_handler,
        )
    )

    # Error handler
    app.add_error_handler(error_handler)

    # ─── Start Bot ──────────────────────────────────────────
    logger.info("🟢 Bot is now polling for updates...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
