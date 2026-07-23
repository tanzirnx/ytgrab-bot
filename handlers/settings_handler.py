"""
YTGrab Bot - Extended Settings Handler
Commands: /setquality, /setformat, /setlang, /setthumb, /setsubs, /setnotify, /setfilename, /reset, /mydefaults
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import Config
from models.database import db
from utils.validators import Validators
from utils.constants import SUPPORTED_LANGUAGES
from templates.i18n import I18n


async def setquality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setquality command."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "📺 <b>Set Default Video Quality</b>\n\n"
            "<b>Usage:</b> /setquality <resolution>\n\n"
            "Options: 144, 240, 360, 480, 720, 1080, 1440, 2160, best\n\n"
            "Example: /setquality 720",
            parse_mode=ParseMode.HTML,
        )
        return

    quality = context.args[0].lower().replace("p", "")

    if not Validators.is_valid_resolution(quality):
        await update.message.reply_text(
            "❌ Invalid quality.\n\n"
            "Valid: 144, 240, 360, 480, 720, 1080, 1440, 2160, best",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.update_user_preference(user_id, "default_video_resolution", quality)
    await update.message.reply_text(
        f"✅ Default quality set to <b>{quality}p</b>",
        parse_mode=ParseMode.HTML,
    )


async def setformat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setformat command."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "🎵 <b>Set Default Format</b>\n\n"
            "<b>Usage:</b> /setformat <format>\n\n"
            "Audio: mp3, m4a, flac, ogg, wav, opus\n"
            "Video: mp4, webm, mkv\n\n"
            "Example: /setformat mp3",
            parse_mode=ParseMode.HTML,
        )
        return

    fmt = context.args[0].lower()

    if not Validators.is_valid_format(fmt):
        await update.message.reply_text(
            "❌ Invalid format.\n\n"
            "Valid: mp3, m4a, flac, ogg, wav, opus, mp4, webm, mkv",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.update_user_preference(user_id, "default_format", fmt)
    await update.message.reply_text(
        f"✅ Default format set to <b>{fmt.upper()}</b>",
        parse_mode=ParseMode.HTML,
    )


async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlang command."""
    user_id = update.effective_user.id

    if not context.args:
        langs = "\n".join(f"  {code} - {name}" for code, name in SUPPORTED_LANGUAGES.items())
        await update.message.reply_text(
            f"🌐 <b>Set Language</b>\n\n"
            f"<b>Usage:</b> /setlang <code>\n\n"
            f"Available:\n{langs}\n\n"
            f"Example: /setlang hi",
            parse_mode=ParseMode.HTML,
        )
        return

    lang = context.args[0].lower()

    if lang not in SUPPORTED_LANGUAGES:
        await update.message.reply_text(
            f"❌ Language '{lang}' not supported.\n\n"
            f"Available: {', '.join(SUPPORTED_LANGUAGES.keys())}",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.update_user_preference(user_id, "language", lang)
    welcome = I18n.get("welcome", lang, name=update.effective_user.first_name)
    await update.message.reply_text(
        f"✅ {welcome}\n\n"
        f"Language set to <b>{SUPPORTED_LANGUAGES[lang]}</b>",
        parse_mode=ParseMode.HTML,
    )


async def setthumb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setthumb command."""
    user_id = update.effective_user.id

    if context.args and context.args[0].lower() in ("on", "off"):
        value = 1 if context.args[0].lower() == "on" else 0
    else:
        user = await db.get_user(user_id)
        current = user.get("auto_thumbnail", 1) if user else 1
        value = 0 if current else 1

    await db.update_user_preference(user_id, "auto_thumbnail", value)
    status = "✅ ON" if value else "❌ OFF"
    await update.message.reply_text(
        f"🖼 Auto Thumbnail: <b>{status}</b>",
        parse_mode=ParseMode.HTML,
    )


async def setsubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setsubs command."""
    user_id = update.effective_user.id

    if context.args and context.args[0].lower() in ("on", "off"):
        value = 1 if context.args[0].lower() == "on" else 0
    else:
        user = await db.get_user(user_id)
        current = user.get("auto_subtitles", 0) if user else 0
        value = 0 if current else 1

    await db.update_user_preference(user_id, "auto_subtitles", value)
    status = "✅ ON" if value else "❌ OFF"
    await update.message.reply_text(
        f"📝 Auto Subtitles: <b>{status}</b>",
        parse_mode=ParseMode.HTML,
    )


async def setnotify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setnotify command."""
    user_id = update.effective_user.id

    if context.args and context.args[0].lower() in ("on", "off"):
        value = 1 if context.args[0].lower() == "on" else 0
    else:
        user = await db.get_user(user_id)
        current = user.get("notifications", 1) if user else 1
        value = 0 if current else 1

    await db.update_user_preference(user_id, "notifications", value)
    status = "✅ ON" if value else "❌ OFF"
    await update.message.reply_text(
        f"🔔 Notifications: <b>{status}</b>",
        parse_mode=ParseMode.HTML,
    )


async def setfilename_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setfilename command."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "📄 <b>Set Filename Template</b>\n\n"
            "<b>Usage:</b> /setfilename <template>\n\n"
            "<b>Variables:</b>\n"
            "  {title} - Video title\n"
            "  {ext} - File extension\n"
            "  {uploader} - Channel name\n"
            "  {duration} - Duration\n"
            "  {id} - Video ID\n\n"
            "<b>Default:</b> <code>{title}.{ext}</code>\n"
            "<b>Example:</b> <code>{uploader} - {title}.{ext}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    template = " ".join(context.args)
    await db.update_user_preference(user_id, "filename_template", template)
    await update.message.reply_text(
        f"✅ Filename template set to:\n<code>{template}</code>",
        parse_mode=ParseMode.HTML,
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command - reset all settings."""
    user_id = update.effective_user.id

    defaults = {
        'default_format': 'mp3',
        'default_quality': 'best',
        'default_audio_bitrate': 320,
        'default_video_resolution': '1080',
        'auto_thumbnail': 1,
        'auto_subtitles': 0,
        'subtitle_language': 'en',
        'filename_template': '{title}.{ext}',
        'notifications': 1,
        'language': 'en',
    }

    for key, value in defaults.items():
        await db.update_user_preference(user_id, key, value)

    await update.message.reply_text(
        "🔄 <b>All settings reset to defaults!</b>\n\n"
        "🎵 Format: MP3\n"
        "📺 Quality: 1080p\n"
        "🎧 Bitrate: 320kbps\n"
        "🖼 Thumbnail: ON\n"
        "📝 Subtitles: OFF\n"
        "🔔 Notifications: ON\n"
        "🌐 Language: English",
        parse_mode=ParseMode.HTML,
    )


async def mydefaults_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mydefaults command - show current settings."""
    user_id = update.effective_user.id
    user = await db.get_user(user_id)

    if not user:
        await update.message.reply_text("No settings found. Use /start first.")
        return

    text = (
        f"⚙️ <b>Your Current Settings</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎵 Default Format: <b>{user.get('default_format', 'mp3').upper()}</b>\n"
        f"📺 Default Quality: <b>{user.get('default_video_resolution', '1080')}p</b>\n"
        f"🎧 Audio Bitrate: <b>{user.get('default_audio_bitrate', 320)}kbps</b>\n"
        f"🖼 Auto Thumbnail: <b>{'✅ ON' if user.get('auto_thumbnail', 1) else '❌ OFF'}</b>\n"
        f"📝 Auto Subtitles: <b>{'✅ ON' if user.get('auto_subtitles', 0) else '❌ OFF'}</b>\n"
        f"📝 Subtitle Lang: <b>{user.get('subtitle_language', 'en').upper()}</b>\n"
        f"🔔 Notifications: <b>{'✅ ON' if user.get('notifications', 1) else '❌ OFF'}</b>\n"
        f"🌐 Language: <b>{SUPPORTED_LANGUAGES.get(user.get('language', 'en'), 'English')}</b>\n"
        f"📄 Filename: <code>{user.get('filename_template', '{title}.{ext}')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📥 Downloads Today: <b>{user.get('downloads_today', 0)}</b>\n"
        f"📥 Total Downloads: <b>{user.get('total_downloads', 0)}</b>\n\n"
        f"💡 Use /reset to restore defaults"
    )

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
