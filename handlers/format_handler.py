"""
YTGrab Bot - Format Handler (Phase 3)
Commands: /format, /age, /speed
"""

import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from loguru import logger

from config import Config
from services.downloader import downloader
from utils.helpers import Helpers
from utils.validators import Validators

import yt_dlp


async def format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /format command - list all available formats."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📊 <b>Usage:</b> /format <url>\n\n"
            "Lists all available formats and qualities for a video.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "📊 <i>Fetching available formats...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        def _get_formats():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _get_formats)

        if not data:
            await msg.edit_text("❌ Could not fetch format info.")
            return

        title = Helpers.escape_html(data.get("title", "Unknown")[:60])
        formats = data.get("formats", [])

        text = f"📊 <b>Available Formats: {title}</b>\n\n"

        # Video+Audio combined formats
        text += "🎬 <b>Video + Audio:</b>\n"
        text += "<code>ID  | Ext | Resolution | Size</code>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n"

        video_audio_formats = []
        video_only_formats = []
        audio_only_formats = []

        for f in formats:
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            height = f.get("height")
            ext = f.get("ext", "?")
            filesize = f.get("filesize", 0) or f.get("filesize_approx", 0) or 0
            format_id = f.get("format_id", "?")
            tbr = f.get("tbr", 0) or 0
            abr = f.get("abr", 0) or 0

            size_str = Helpers.format_filesize(filesize) if filesize else "?"

            if vcodec != "none" and acodec != "none" and height:
                video_audio_formats.append(
                    f"  {format_id:>5} | {ext:<4} | {height}p | {size_str}"
                )
            elif vcodec != "none" and height:
                video_only_formats.append(
                    f"  {format_id:>5} | {ext:<4} | {height}p | {size_str}"
                )
            elif acodec != "none":
                audio_only_formats.append(
                    f"  {format_id:>5} | {ext:<4} | {int(abr)}kbps | {size_str}"
                )

        # Show combined
        for line in video_audio_formats[:10]:
            text += f"<code>{line}</code>\n"

        if video_only_formats:
            text += f"\n🎥 <b>Video Only:</b>\n"
            for line in video_only_formats[:8]:
                text += f"<code>{line}</code>\n"

        if audio_only_formats:
            text += f"\n🎵 <b>Audio Only:</b>\n"
            for line in audio_only_formats[:8]:
                text += f"<code>{line}</code>\n"

        total = len(formats)
        text += f"\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 Total formats: {total}"

        # Download buttons
        buttons = [
            [
                InlineKeyboardButton("🎵 Audio", callback_data=f"action_audio|{url}"),
                InlineKeyboardButton("🎬 Video", callback_data=f"action_video|{url}"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_start")],
        ]

        await msg.edit_text(
            Helpers.truncate(text, 4000),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        logger.error(f"Format error: {e}")
        await msg.edit_text("❌ Failed to fetch formats.", parse_mode=ParseMode.HTML)


async def age_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /age command - check if video is age-restricted."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "🔞 <b>Usage:</b> /age <url>\n\nChecks if a video is age-restricted.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text("🔞 <i>Checking...</i>", parse_mode=ParseMode.HTML)

    try:
        def _check():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _check)

        if not data:
            await msg.edit_text("❌ Could not fetch video info.")
            return

        title = Helpers.escape_html(data.get("title", "Unknown")[:60])
        age_limit = data.get("age_limit", 0)
        is_live = data.get("is_live", False)

        if age_limit and age_limit >= 18:
            text = (
                f"🔞 <b>Age-Restricted Video</b>\n\n"
                f"🎬 {title}\n"
                f"⚠️ Age Limit: <b>{age_limit}+</b>\n\n"
                f"❌ This video cannot be downloaded by the bot\n"
                f"due to age restrictions."
            )
        elif age_limit and age_limit > 0:
            text = (
                f"⚠️ <b>Age-Restricted Video</b>\n\n"
                f"🎬 {title}\n"
                f"🔞 Age Limit: <b>{age_limit}+</b>\n\n"
                f"⚡ Download may still work."
            )
        else:
            text = (
                f"✅ <b>No Age Restriction</b>\n\n"
                f"🎬 {title}\n"
                f"👁 This video is available to all ages.\n"
                f"{'🔴 LIVE' if is_live else '📹 Regular video'}\n\n"
                f"⚡ You can download this video!"
            )

        buttons = [
            [
                InlineKeyboardButton("🎵 Audio", callback_data=f"action_audio|{url}"),
                InlineKeyboardButton("🎬 Video", callback_data=f"action_video|{url}"),
            ],
        ] if age_limit == 0 else []

        await msg.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        )

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if "age" in error_msg:
            await msg.edit_text(
                "🔞 <b>Age-Restricted</b>\n\n"
                "This video requires age verification.\n"
                "❌ Cannot be downloaded by the bot.",
                parse_mode=ParseMode.HTML,
            )
        else:
            await msg.edit_text("❌ Could not check video.", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Age check error: {e}")
        await msg.edit_text("❌ Check failed.", parse_mode=ParseMode.HTML)


async def speed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /speed command - test download speed."""
    msg = await update.message.reply_text(
        "⚡ <b>Testing Download Speed...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        # Use a small, reliable test video
        test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" (19s)

        start_time = time.time()

        import yt_dlp
        from pathlib import Path

        test_dir = Config.DOWNLOADS_DIR / "speed_test"
        test_dir.mkdir(parents=True, exist_ok=True)

        opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "worst",
            "outtmpl": str(test_dir / "speed_test.%(ext)s"),
            "noplaylist": True,
        }

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([test_url])

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download)

        elapsed = time.time() - start_time

        # Find downloaded file
        file_size = 0
        for f in test_dir.iterdir():
            if f.is_file():
                file_size = f.stat().st_size
                f.unlink()
                break

        try:
            test_dir.rmdir()
        except Exception:
            pass

        speed_mbps = (file_size / (1024 * 1024)) / elapsed if elapsed > 0 else 0

        text = (
            f"⚡ <b>Speed Test Results</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 Download Speed: <b>{speed_mbps:.2f} MB/s</b>\n"
            f"📦 Test File: {Helpers.format_filesize(file_size)}\n"
            f"⏱ Time: {elapsed:.2f}s\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        if speed_mbps > 10:
            text += "🚀 Excellent! Very fast downloads."
        elif speed_mbps > 5:
            text += "✅ Good speed for most downloads."
        elif speed_mbps > 1:
            text += "⚠️ Moderate speed. Large files may take time."
        else:
            text += "🐌 Slow connection. Consider a better server."

        await msg.edit_text(text, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Speed test error: {e}")
        await msg.edit_text(
            "❌ Speed test failed. Server may be under load.",
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
