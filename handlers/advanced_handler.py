"""
YTGrab Bot - Advanced Handler (Phase 3)
Commands: /audiobook, /live, /chapters, /sponsorblock
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
from services.sponsorblock_service import sponsorblock_service
from utils.helpers import Helpers
from utils.validators import Validators

import yt_dlp


async def audiobook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /audiobook command - download long audio with chapters."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📚 <b>Usage:</b> /audiobook <url>\n\n"
            "Downloads audio and splits into chapters.\n"
            "Best for long videos, lectures, podcasts.\n\n"
            "Example: /audiobook https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "📚 <b>Downloading Audiobook...</b>\n\n"
        "⏳ Extracting audio & chapters...\n"
        "This may take a while for long videos.",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_AUDIO)

        # Download audio
        file_path = await downloader.download_audio(
            url=url, user_id=user_id, format="mp3", bitrate=192,
        )

        if not file_path or not file_path.exists():
            await msg.edit_text("❌ Download failed.", parse_mode=ParseMode.HTML)
            return

        # Get chapters
        info = await downloader.extract_info(url)
        chapters = await _get_chapters(url)

        file_size = file_path.stat().st_size
        max_size = Config.TELEGRAM_MAX_FILE_SIZE_LOCAL if Config.USE_LOCAL_API else Config.TELEGRAM_MAX_FILE_SIZE

        if file_size > max_size:
            await msg.edit_text(
                f"⚠️ File too large ({Helpers.format_filesize(file_size)}).\n"
                f"Max: {Helpers.format_filesize(max_size)}",
                parse_mode=ParseMode.HTML,
            )
            file_manager.cleanup_user_files(user_id)
            return

        if chapters and len(chapters) > 1:
            # Split into chapters
            await msg.edit_text(
                f"📚 <b>Splitting into {len(chapters)} chapters...</b>",
                parse_mode=ParseMode.HTML,
            )

            parts = await file_manager.split_audio_chapters(file_path, chapters)

            if parts:
                for i, part in enumerate(parts):
                    chapter_title = chapters[i].get("title", f"Chapter {i+1}")
                    with open(part, "rb") as f:
                        await update.effective_chat.send_audio(
                            audio=f,
                            filename=part.name,
                            caption=(
                                f"📚 <b>{Helpers.escape_html(chapter_title[:200])}</b>\n"
                                f"📖 Chapter {i+1}/{len(chapters)}\n\n"
                                f"⚡ @YTGrabDownBot"
                            ),
                            parse_mode=ParseMode.HTML,
                        )
                    await asyncio.sleep(0.5)

                await msg.edit_text(
                    f"✅ <b>Audiobook Complete!</b>\n\n"
                    f"📚 {len(parts)} chapters sent.",
                    parse_mode=ParseMode.HTML,
                )
            else:
                # Fallback: send as single file
                await _send_single_audio(update, file_path, info)
                await msg.edit_text("✅ <b>Audio sent!</b> (No chapters found)", parse_mode=ParseMode.HTML)
        else:
            # No chapters - send as single file
            await _send_single_audio(update, file_path, info)
            await msg.edit_text(
                "✅ <b>Audio sent!</b>\n\n💡 No chapters detected in this video.",
                parse_mode=ParseMode.HTML,
            )

        await db.increment_downloads(user_id)

    except Exception as e:
        logger.error(f"Audiobook error: {e}")
        await msg.edit_text("❌ Audiobook download failed.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /live command - download ongoing livestream."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "🔴 <b>Usage:</b> /live <url>\n\n"
            "Downloads the current portion of an ongoing livestream.\n"
            "Example: /live https://youtube.com/live/xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "🔴 <b>Checking Livestream...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        info = await downloader.extract_info(url)

        if info.error:
            await msg.edit_text("❌ Could not access this stream.", parse_mode=ParseMode.HTML)
            return

        if not info.is_live:
            await msg.edit_text(
                "📹 <b>This is not a live stream.</b>\n\n"
                "Use /mp4 or /mp3 to download regular videos.",
                parse_mode=ParseMode.HTML,
            )
            return

        await msg.edit_text(
            f"🔴 <b>Livestream Detected!</b>\n\n"
            f"🎬 {Helpers.escape_html(info.title)}\n"
            f"👤 {Helpers.escape_html(info.uploader)}\n\n"
            f"⬇️ Downloading current portion...\n"
            f"⚠️ This will capture the available stream data.",
            parse_mode=ParseMode.HTML,
        )

        # Download livestream (will get available portion)
        file_path = await downloader.download_video(
            url=url, user_id=user_id,
            resolution="720", format="mp4",
        )

        if file_path and file_path.exists():
            file_size = file_path.stat().st_size
            max_size = Config.TELEGRAM_MAX_FILE_SIZE_LOCAL if Config.USE_LOCAL_API else Config.TELEGRAM_MAX_FILE_SIZE

            if file_size <= max_size:
                await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
                with open(file_path, "rb") as f:
                    await update.effective_chat.send_video(
                        video=f,
                        filename=file_path.name,
                        caption=(
                            f"🔴 <b>Livestream Capture</b>\n"
                            f"🎬 {Helpers.escape_html(info.title[:100])}\n"
                            f"📦 {Helpers.format_filesize(file_size)}\n\n"
                            f"⚡ @YTGrabDownBot"
                        ),
                        parse_mode=ParseMode.HTML,
                        supports_streaming=True,
                    )
                await msg.edit_text("✅ <b>Livestream captured!</b>", parse_mode=ParseMode.HTML)
            else:
                await msg.edit_text(
                    f"⚠️ Stream too large ({Helpers.format_filesize(file_size)}).",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await msg.edit_text("❌ Could not capture stream.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Live error: {e}")
        await msg.edit_text("❌ Livestream download failed.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def chapters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chapters command - list video chapters."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📑 <b>Usage:</b> /chapters <url>\n\nLists video chapters/timestamps.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text("📑 <i>Fetching chapters...</i>", parse_mode=ParseMode.HTML)

    try:
        chapters = await _get_chapters(url)
        info = await downloader.extract_info(url)

        if not chapters:
            await msg.edit_text(
                "📑 <b>No chapters found.</b>\n\n"
                "This video doesn't have chapter markers.\n"
                "Chapters are usually set by the uploader in the description.",
                parse_mode=ParseMode.HTML,
            )
            return

        title = Helpers.escape_html(info.title[:60]) if not info.error else "Video"
        text = f"📑 <b>Chapters: {title}</b>\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, ch in enumerate(chapters):
            start = Helpers.format_duration(int(ch.get("start_time", 0)))
            ch_title = Helpers.escape_html(ch.get("title", f"Chapter {i+1}")[:60])
            text += f"  {i+1}. ⏱ <code>{start}</code> - {ch_title}\n"

        text += f"\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 Total chapters: {len(chapters)}\n\n"
        text += f"💡 Use /audiobook <url> to download as separate chapters"

        await msg.edit_text(
            Helpers.truncate(text, 4000),
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        logger.error(f"Chapters error: {e}")
        await msg.edit_text("❌ Failed to fetch chapters.", parse_mode=ParseMode.HTML)


async def sponsorblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sponsorblock command - toggle SponsorBlock."""
    user_id = update.effective_user.id

    user = await db.get_user(user_id)
    # Store sponsorblock preference (using auto_subtitles field as workaround, or add new field)
    # For now, just show info
    await update.message.reply_text(
        "🛡️ <b>SponsorBlock Integration</b>\n\n"
        "SponsorBlock automatically skips sponsor segments in videos.\n\n"
        "<b>Categories:</b>\n"
        "  • Sponsor (paid promotion)\n"
        "  • Self-promotion\n"
        "  • Interaction reminder\n"
        "  • Intro/Outro\n"
        "  • Filler/Joke\n\n"
        "⚙️ <b>Status:</b> Enabled by default\n\n"
        "💡 When downloading, sponsor segments are automatically removed.\n"
        "Use /settings to toggle.",
        parse_mode=ParseMode.HTML,
    )


# ─── Internal Helpers ───────────────────────────────────────

async def _get_chapters(url: str) -> list:
    """Extract chapters from video."""
    def _extract():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _extract)

        if data and data.get("chapters"):
            return data["chapters"]
        return []
    except Exception:
        return []


async def _send_single_audio(update, file_path, info):
    """Send a single audio file."""
    file_size = file_path.stat().st_size
    title = info.title if info and not info.error else file_path.stem

    with open(file_path, "rb") as f:
        await update.effective_chat.send_audio(
            audio=f,
            filename=file_path.name,
            caption=(
                f"📚 <b>{Helpers.escape_html(title[:200])}</b>\n"
                f"📦 {Helpers.format_filesize(file_size)}\n\n"
                f"⚡ @YTGrabDownBot"
            ),
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
