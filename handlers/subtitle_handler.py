"""
YTGrab Bot - Subtitle Handler (Phase 3)
Commands: /subs, /subslist, /subslang
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from loguru import logger

from config import Config
from models.database import db
from services.downloader import downloader
from services.file_manager import file_manager
from utils.helpers import Helpers
from utils.validators import Validators

import yt_dlp


async def subs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subs command - download subtitles."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📝 <b>Usage:</b> /subs <url> [language]\n\n"
            "Examples:\n"
            "  /subs https://youtube.com/watch?v=xyz\n"
            "  /subs https://youtube.com/watch?v=xyz hi\n"
            "  /subs https://youtube.com/watch?v=xyz en srt",
            parse_mode=ParseMode.HTML,
        )
        return

    # Parse optional language and format
    lang = "en"
    sub_format = "srt"
    if context.args and len(context.args) > 1:
        lang = context.args[1].lower()
    if context.args and len(context.args) > 2:
        sub_format = context.args[2].lower()

    if sub_format not in Config.SUBTITLE_FORMATS:
        sub_format = "srt"

    msg = await update.message.reply_text(
        f"📝 <b>Downloading Subtitles...</b>\n\n"
        f"🌐 Language: {lang.upper()}\n"
        f"📄 Format: {sub_format.upper()}\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_DOCUMENT)

        file_path = await downloader.download_subtitles(
            url=url, user_id=user_id, lang=lang, format=sub_format
        )

        if file_path and file_path.exists():
            file_size = file_path.stat().st_size
            with open(file_path, "rb") as f:
                await update.effective_chat.send_document(
                    document=f,
                    filename=file_path.name,
                    caption=(
                        f"📝 <b>Subtitles</b>\n"
                        f"🌐 Language: {lang.upper()}\n"
                        f"📄 Format: {sub_format.upper()}\n"
                        f"📦 Size: {Helpers.format_filesize(file_size)}\n\n"
                        f"⚡ @YTGrabDownBot"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            await msg.edit_text("✅ <b>Subtitles downloaded!</b>", parse_mode=ParseMode.HTML)
        else:
            # Show available languages
            await msg.edit_text(
                f"❌ <b>No subtitles found for '{lang.upper()}'</b>\n\n"
                f"Use /subslist <url> to see available languages.",
                parse_mode=ParseMode.HTML,
            )

    except Exception as e:
        logger.error(f"Subs error: {e}")
        await msg.edit_text("❌ Failed to download subtitles.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def subslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subslist command - list available subtitle languages."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📋 <b>Usage:</b> /subslist <url>\n\n"
            "Lists all available subtitle languages for a video.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "📋 <i>Fetching subtitle list...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        def _get_subs():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _get_subs)

        if not data:
            await msg.edit_text("❌ Could not fetch video info.")
            return

        title = Helpers.escape_html(data.get("title", "Unknown")[:60])
        subtitles = data.get("subtitles", {})
        auto_captions = data.get("automatic_captions", {})

        text = f"📋 <b>Subtitles for: {title}</b>\n\n"

        # Manual subtitles
        if subtitles:
            text += f"📝 <b>Manual Subtitles ({len(subtitles)}):</b>\n"
            for lang in sorted(subtitles.keys())[:30]:
                formats = [f.get("ext", "?") for f in subtitles[lang][:3]]
                text += f"  • {lang.upper()} ({', '.join(formats)})\n"
            text += "\n"

        # Auto-generated
        if auto_captions:
            text += f"🤖 <b>Auto-Generated ({len(auto_captions)}):</b>\n"
            auto_langs = sorted(auto_captions.keys())[:20]
            text += f"  {', '.join(l.upper() for l in auto_langs)}\n"
            if len(auto_captions) > 20:
                text += f"  ... and {len(auto_captions) - 20} more\n"
            text += "\n"

        if not subtitles and not auto_captions:
            text += "❌ No subtitles available for this video.\n"

        text += "\n💡 Download: /subs <url> <lang>\n"
        text += "Example: /subs <url> en"

        await msg.edit_text(
            Helpers.truncate(text, 4000),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Subslist error: {e}")
        await msg.edit_text("❌ Failed to fetch subtitle list.", parse_mode=ParseMode.HTML)


async def subslang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subslang command - set default subtitle language."""
    user_id = update.effective_user.id

    if not context.args:
        user = await db.get_user(user_id)
        current = user.get("subtitle_language", "en") if user else "en"
        await update.message.reply_text(
            f"📝 Current subtitle language: <b>{current.upper()}</b>\n\n"
            f"<b>Usage:</b> /subslang <code>\n"
            f"Examples: /subslang en, /subslang hi, /subslang es\n\n"
            f"Common codes: en, hi, es, fr, ar, pt, ru, ja, ko, zh, de, it",
            parse_mode=ParseMode.HTML,
        )
        return

    lang = context.args[0].lower()
    await db.update_user_preference(user_id, "subtitle_language", lang)
    await update.message.reply_text(
        f"✅ Default subtitle language set to <b>{lang.upper()}</b>",
        parse_mode=ParseMode.HTML,
    )


def _get_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if context.args:
        url = Validators.extract_url(context.args[0])
        if url:
            return url
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            return Validators.extract_url(parts[1])
    return None
