"""
YTGrab Bot - Audio Handler
All audio format commands: /m4a, /flac, /ogg, /wav, /opus, /audiobook
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import Config
from models.database import db
from services.downloader import downloader
from services.file_manager import file_manager
from utils.helpers import Helpers
from utils.validators import Validators
from handlers.download_handler import _execute_audio_download, _get_url_from_command


async def m4a_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /m4a command."""
    await _audio_format_command(update, context, "m4a", 256)

async def flac_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /flac command."""
    await _audio_format_command(update, context, "flac", 0)

async def ogg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ogg command."""
    await _audio_format_command(update, context, "ogg", 256)

async def wav_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wav command."""
    await _audio_format_command(update, context, "wav", 0)

async def opus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /opus command."""
    await _audio_format_command(update, context, "opus", 128)

async def aac_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /aac command."""
    await _audio_format_command(update, context, "aac", 256)


async def _audio_format_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE,
    format: str, bitrate: int
):
    """Generic audio format download command."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            f"🎵 <b>Usage:</b> /{format} <url>\n\n"
            f"Example: /{format} https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    # Check rate limit
    downloads_today = await db.get_downloads_today(user_id)
    if downloads_today >= Config.RATE_LIMIT_PER_DAY:
        await update.message.reply_text(
            f"⏳ Daily limit reached ({Config.RATE_LIMIT_PER_DAY}). Try again tomorrow.",
            parse_mode=ParseMode.HTML,
        )
        return

    await _execute_audio_download(
        update=update,
        url=url,
        user_id=user_id,
        format=format,
        bitrate=bitrate,
    )
