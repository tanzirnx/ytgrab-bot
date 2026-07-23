"""
YTGrab Bot - Start & Help Handlers
Handles /start, /help, /faq, /settings, and callback queries.
"""

import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from loguru import logger

from config import Config
from models.database import db
from utils.keyboards import Keyboards
from templates.messages import Messages


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_id = user.id

    # Check if banned
    if await db.is_banned(user_id):
        await update.message.reply_text(
            Messages.ERROR_BANNED, parse_mode=ParseMode.HTML
        )
        return

    # Create/update user in database
    await db.create_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
    )

    # Send welcome message
    welcome_text = Messages.WELCOME.format(name=user.first_name)
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.start_menu(),
        disable_web_page_preview=True,
    )

    logger.info(f"👤 User started: {user.first_name} (@{user.username}) [ID: {user_id}]")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        Messages.HELP,
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.back_to_start(),
        disable_web_page_preview=True,
    )


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /faq command."""
    await update.message.reply_text(
        Messages.FAQ,
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.back_to_start(),
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user_id = update.effective_user.id
    user_prefs = await db.get_user(user_id)

    await update.message.reply_text(
        "⚙️ <b>Settings</b>\n\nTap a button to change:",
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.settings_menu(user_prefs),
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    ms = round((end_time - start_time) * 1000)

    await msg.edit_text(
        Messages.PING_RESPONSE.format(ms=ms),
        parse_mode=ParseMode.HTML,
    )


async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /version command."""
    import sys
    import yt_dlp

    await update.message.reply_text(
        Messages.VERSION_INFO.format(
            ytdlp_version=yt_dlp.version.__version__,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        parse_mode=ParseMode.HTML,
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # ─── Menu Navigation ────────────────────────────────────

    if data == "back_start":
        await query.edit_message_text(
            Messages.WELCOME.format(name=query.from_user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.start_menu(),
            disable_web_page_preview=True,
        )
        return

    if data == "menu_features":
        await query.edit_message_text(
            Messages.FEATURES,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.back_to_start(),
        )
        return

    if data == "menu_howto":
        await query.edit_message_text(
            Messages.HOW_TO,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.back_to_start(),
            disable_web_page_preview=True,
        )
        return

    if data == "menu_faq":
        await query.edit_message_text(
            Messages.FAQ,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.back_to_start(),
        )
        return

    if data == "menu_settings":
        user_prefs = await db.get_user(user_id)
        await query.edit_message_text(
            "⚙️ <b>Settings</b>\n\nTap a button to change:",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(user_prefs),
        )
        return

    # ─── Media Action Menu ──────────────────────────────────

    if data.startswith("action_menu|"):
        url = data.split("|", 1)[1]
        from handlers.download_handler import _show_media_info
        await _show_media_info(query, url)
        return

    if data.startswith("action_audio|"):
        url = data.split("|", 1)[1]
        await query.edit_message_text(
            "🎵 <b>Select Audio Format:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.audio_format_menu(url),
        )
        return

    if data.startswith("action_video|"):
        url = data.split("|", 1)[1]
        await query.edit_message_text(
            "🎬 <b>Select Video Quality:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.video_quality_menu(url),
        )
        return

    if data.startswith("action_info|"):
        url = data.split("|", 1)[1]
        from handlers.download_handler import _show_detailed_info
        await _show_detailed_info(query, url)
        return

    if data.startswith("action_thumb|"):
        url = data.split("|", 1)[1]
        from handlers.download_handler import _download_thumbnail
        await _download_thumbnail(query, url, user_id)
        return

    if data.startswith("action_subs|"):
        url = data.split("|", 1)[1]
        await query.edit_message_text(
            "📝 <b>Select Subtitle Language:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.subtitle_lang_menu(url),
        )
        return

    if data.startswith("action_options|"):
        url = data.split("|", 1)[1]
        await query.edit_message_text(
            "⚙️ <b>Advanced Options</b>\n\n"
            "🔹 Use /clip <url> <start>-<end> for time range\n"
            "🔹 Use /metadata <url> for JSON metadata\n"
            "🔹 Use /description <url> for description\n"
            "🔹 Use /format <url> for all formats\n",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.media_action_menu(url),
        )
        return

    # ─── Download Triggers ──────────────────────────────────

    if data.startswith("dl_mp3_") or data.startswith("dl_m4a_") or \
       data.startswith("dl_flac_") or data.startswith("dl_ogg_") or \
       data.startswith("dl_wav_") or data.startswith("dl_opus_"):
        from handlers.download_handler import _handle_audio_download
        await _handle_audio_download(query, data, user_id)
        return

    if data.startswith("dl_vid_"):
        from handlers.download_handler import _handle_video_download
        await _handle_video_download(query, data, user_id)
        return

    if data.startswith("dl_sub_"):
        from handlers.download_handler import _handle_subtitle_download
        await _handle_subtitle_download(query, data, user_id)
        return

    if data.startswith("search_dl|"):
        url = data.split("|", 1)[1]
        from handlers.download_handler import _show_media_info
        await _show_media_info(query, url)
        return

    # ─── Settings Toggles ───────────────────────────────────

    if data == "set_format":
        await query.edit_message_text(
            "🎵 <b>Select Default Format:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.format_selection(),
        )
        return

    if data == "set_quality":
        await query.edit_message_text(
            "📺 <b>Select Default Quality:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.quality_selection(),
        )
        return

    if data == "set_thumb":
        user_prefs = await db.get_user(user_id)
        current = user_prefs.get("auto_thumbnail", 1) if user_prefs else 1
        new_val = 0 if current else 1
        await db.update_user_preference(user_id, "auto_thumbnail", new_val)
        status = "✅ Enabled" if new_val else "❌ Disabled"
        await query.edit_message_text(
            Messages.SETTINGS_UPDATED.format(key="Auto Thumbnail", value=status),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    if data == "set_subs":
        user_prefs = await db.get_user(user_id)
        current = user_prefs.get("auto_subtitles", 0) if user_prefs else 0
        new_val = 0 if current else 1
        await db.update_user_preference(user_id, "auto_subtitles", new_val)
        status = "✅ Enabled" if new_val else "❌ Disabled"
        await query.edit_message_text(
            Messages.SETTINGS_UPDATED.format(key="Auto Subtitles", value=status),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    if data == "set_notify":
        user_prefs = await db.get_user(user_id)
        current = user_prefs.get("notifications", 1) if user_prefs else 1
        new_val = 0 if current else 1
        await db.update_user_preference(user_id, "notifications", new_val)
        status = "✅ Enabled" if new_val else "❌ Disabled"
        await query.edit_message_text(
            Messages.SETTINGS_UPDATED.format(key="Notifications", value=status),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    if data == "set_reset":
        # Reset all preferences to defaults
        defaults = {
            'default_format': 'mp3',
            'default_quality': 'best',
            'default_audio_bitrate': 320,
            'default_video_resolution': '1080',
            'auto_thumbnail': 1,
            'auto_subtitles': 0,
            'notifications': 1,
        }
        for key, value in defaults.items():
            await db.update_user_preference(user_id, key, value)
        await query.edit_message_text(
            Messages.SETTINGS_RESET,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    # ─── Preference Selections ──────────────────────────────

    if data.startswith("pref_format_"):
        fmt = data.replace("pref_format_", "")
        await db.update_user_preference(user_id, "default_format", fmt)
        await query.edit_message_text(
            Messages.SETTINGS_UPDATED.format(key="Default Format", value=fmt.upper()),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    if data.startswith("pref_quality_"):
        quality = data.replace("pref_quality_", "")
        await db.update_user_preference(user_id, "default_video_resolution", quality)
        await query.edit_message_text(
            Messages.SETTINGS_UPDATED.format(key="Default Quality", value=f"{quality}p"),
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.settings_menu(await db.get_user(user_id)),
        )
        return

    # ─── Fallback ───────────────────────────────────────────
    logger.warning(f"Unhandled callback: {data}")
