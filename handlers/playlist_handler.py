"""
YTGrab Bot - Playlist Handler
Handles playlist downloads, range selection, and playlist info.
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
from templates.messages import Messages

import yt_dlp


async def playlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pl or /playlist command."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📁 <b>Usage:</b> /pl <playlist_url>\n\n"
            "Example: /pl https://youtube.com/playlist?list=PLxyz",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "📁 <i>Fetching playlist info...</i>",
        parse_mode=ParseMode.HTML,
    )

    # Extract playlist info
    info = await _get_playlist_info(url)

    if not info or info.get("error"):
        await msg.edit_text(
            "❌ <b>Could not fetch playlist.</b>\n\n"
            "Make sure the URL is a valid playlist link.\n"
            "Example: <code>https://youtube.com/playlist?list=PLxyz</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    title = Helpers.escape_html(info.get("title", "Unknown Playlist"))
    count = info.get("count", 0)
    entries = info.get("entries", [])

    # Build text
    text = (
        f"📁 <b>Playlist: {title}</b>\n\n"
        f"📹 Videos: <b>{count}</b>\n"
    )

    # Show first few entries
    if entries:
        text += f"\n<b>First {min(5, len(entries))} videos:</b>\n"
        for i, entry in enumerate(entries[:5]):
            e_title = Helpers.escape_html(entry.get("title", "Unknown")[:50])
            e_dur = Helpers.format_duration(entry.get("duration", 0))
            text += f"  {i+1}. {e_title} ({e_dur})\n"

    if count > Config.MAX_PLAYLIST_ITEMS:
        text += f"\n⚠️ Playlist has {count} videos. Max allowed: {Config.MAX_PLAYLIST_ITEMS}.\n"
        text += f"Only first {Config.MAX_PLAYLIST_ITEMS} will be downloaded.\n"

    text += "\n⬇️ Choose download option:"

    # Build buttons
    buttons = [
        [
            InlineKeyboardButton("⬇️ Download All (Audio)", callback_data=f"pl_all_audio|{url}"),
            InlineKeyboardButton("⬇️ Download All (Video)", callback_data=f"pl_all_video|{url}"),
        ],
        [
            InlineKeyboardButton("📊 Select Range", callback_data=f"pl_range|{url}"),
            InlineKeyboardButton("📋 List Videos", callback_data=f"pl_list|{url}"),
        ],
        [
            InlineKeyboardButton("⬅️ Cancel", callback_data="back_start"),
        ],
    ]

    await msg.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
    )


async def plinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plinfo command - show playlist details."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📋 <b>Usage:</b> /plinfo <playlist_url>",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text("📋 <i>Fetching playlist...</i>", parse_mode=ParseMode.HTML)
    info = await _get_playlist_info(url)

    if not info or info.get("error"):
        await msg.edit_text("❌ Could not fetch playlist info.", parse_mode=ParseMode.HTML)
        return

    title = Helpers.escape_html(info.get("title", "Unknown"))
    count = info.get("count", 0)
    entries = info.get("entries", [])
    total_duration = sum(e.get("duration", 0) or 0 for e in entries)

    text = (
        f"📋 <b>Playlist Information</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📁 <b>Title:</b> {title}\n"
        f"📹 <b>Videos:</b> {count}\n"
        f"⏱ <b>Total Duration:</b> {Helpers.format_duration(total_duration)}\n"
        f"🔗 <b>URL:</b> {url}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    if entries:
        text += "<b>All Videos:</b>\n"
        for i, entry in enumerate(entries[:50]):
            e_title = Helpers.escape_html(entry.get("title", "Unknown")[:60])
            e_dur = Helpers.format_duration(entry.get("duration", 0))
            text += f"  {i+1}. {e_title} ({e_dur})\n"

        if count > 50:
            text += f"\n  ... and {count - 50} more videos"

    await msg.edit_text(
        Helpers.truncate(text, 4000),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def plrange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plrange command - download specific range."""
    user_id = update.effective_user.id

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📊 <b>Usage:</b> /plrange <url> <start-end>\n\n"
            "Example: /plrange https://youtube.com/playlist?list=xyz 1-10",
            parse_mode=ParseMode.HTML,
        )
        return

    url = context.args[0]
    range_str = context.args[1]
    start, end = Validators.parse_playlist_range(range_str)

    await _execute_playlist_download(
        update=update,
        url=url,
        user_id=user_id,
        start=start,
        end=end,
        format_type="audio",
        format_detail="mp3",
    )


async def playlist_callback_handler(query, data: str, user_id: int):
    """Handle playlist-related callback buttons."""
    parts = data.split("|", 1)
    action = parts[0]
    url = parts[1] if len(parts) > 1 else ""

    if action == "pl_all_audio":
        await query.edit_message_text(
            "📁 <b>Downloading Playlist (Audio)...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )
        await _execute_playlist_download(
            update=query, url=url, user_id=user_id,
            start=1, end=Config.MAX_PLAYLIST_ITEMS,
            format_type="audio", format_detail="mp3",
        )

    elif action == "pl_all_video":
        await query.edit_message_text(
            "📁 <b>Downloading Playlist (Video 720p)...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )
        await _execute_playlist_download(
            update=query, url=url, user_id=user_id,
            start=1, end=Config.MAX_PLAYLIST_ITEMS,
            format_type="video", format_detail="720",
        )

    elif action == "pl_range":
        buttons = [
            [
                InlineKeyboardButton("1-10", callback_data=f"pl_r_1_10|{url}"),
                InlineKeyboardButton("11-20", callback_data=f"pl_r_11_20|{url}"),
                InlineKeyboardButton("21-30", callback_data=f"pl_r_21_30|{url}"),
            ],
            [
                InlineKeyboardButton("31-50", callback_data=f"pl_r_31_50|{url}"),
                InlineKeyboardButton("51-100", callback_data=f"pl_r_51_100|{url}"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"pl_back|{url}")],
        ]
        await query.edit_message_text(
            "📊 <b>Select Range:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif action.startswith("pl_r_"):
        # pl_r_1_10|url
        range_parts = action.split("_")
        start = int(range_parts[2])
        end = int(range_parts[3])

        # Ask format
        buttons = [
            [
                InlineKeyboardButton("🎵 MP3 Audio", callback_data=f"pl_rf_audio_{start}_{end}|{url}"),
                InlineKeyboardButton("🎬 720p Video", callback_data=f"pl_rf_video_{start}_{end}|{url}"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"pl_range|{url}")],
        ]
        await query.edit_message_text(
            f"📊 <b>Range: {start}-{end}</b>\n\nSelect format:",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif action.startswith("pl_rf_"):
        # pl_rf_audio_1_10|url
        parts2 = action.split("_")
        fmt_type = parts2[2]
        start = int(parts2[3])
        end = int(parts2[4])

        await query.edit_message_text(
            f"📁 <b>Downloading Playlist ({start}-{end})...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )
        await _execute_playlist_download(
            update=query, url=url, user_id=user_id,
            start=start, end=end,
            format_type=fmt_type,
            format_detail="mp3" if fmt_type == "audio" else "720",
        )

    elif action == "pl_list":
        info = await _get_playlist_info(url)
        if info and info.get("entries"):
            text = f"📋 <b>{Helpers.escape_html(info.get('title', 'Playlist'))}</b>\n\n"
            for i, e in enumerate(info["entries"][:50]):
                t = Helpers.escape_html(e.get("title", "?")[:55])
                d = Helpers.format_duration(e.get("duration", 0))
                text += f"{i+1}. {t} ({d})\n"
            await query.edit_message_text(
                Helpers.truncate(text, 4000),
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.edit_message_text("❌ Could not list videos.", parse_mode=ParseMode.HTML)

    elif action == "pl_back":
        await playlist_command_from_query(query, url)


async def playlist_command_from_query(query, url: str):
    """Re-show playlist menu from callback."""
    info = await _get_playlist_info(url)
    if not info:
        await query.edit_message_text("❌ Error fetching playlist.", parse_mode=ParseMode.HTML)
        return

    title = Helpers.escape_html(info.get("title", "Playlist"))
    count = info.get("count", 0)

    buttons = [
        [
            InlineKeyboardButton("⬇️ All (Audio)", callback_data=f"pl_all_audio|{url}"),
            InlineKeyboardButton("⬇️ All (Video)", callback_data=f"pl_all_video|{url}"),
        ],
        [
            InlineKeyboardButton("📊 Select Range", callback_data=f"pl_range|{url}"),
            InlineKeyboardButton("📋 List Videos", callback_data=f"pl_list|{url}"),
        ],
        [InlineKeyboardButton("⬅️ Cancel", callback_data="back_start")],
    ]

    await query.edit_message_text(
        f"📁 <b>Playlist: {title}</b>\n📹 {count} videos\n\n⬇️ Choose:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ─── Internal Functions ─────────────────────────────────────

async def _get_playlist_info(url: str) -> dict:
    """Fetch playlist information."""
    def _extract():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
            "playlistend": Config.MAX_PLAYLIST_ITEMS,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _extract)

        if not data:
            return {"error": "no_data"}

        entries = []
        for entry in data.get("entries", []):
            if entry:
                entries.append({
                    "title": entry.get("title", "Unknown"),
                    "url": entry.get("url", entry.get("webpage_url", "")),
                    "duration": entry.get("duration", 0),
                    "id": entry.get("id", ""),
                })

        return {
            "title": data.get("title", "Unknown Playlist"),
            "count": data.get("playlist_count", len(entries)),
            "entries": entries,
            "uploader": data.get("uploader", ""),
        }

    except Exception as e:
        logger.error(f"Playlist info error: {e}")
        return {"error": str(e)}


async def _execute_playlist_download(
    update, url: str, user_id: int,
    start: int = 1, end: int = 100,
    format_type: str = "audio",
    format_detail: str = "mp3",
):
    """Execute playlist download sequentially."""
    chat = update.effective_chat if hasattr(update, 'effective_chat') else update.message.chat

    # Get playlist entries
    info = await _get_playlist_info(url)
    if not info or info.get("error"):
        await chat.send_message("❌ Could not fetch playlist.", parse_mode=ParseMode.HTML)
        return

    entries = info.get("entries", [])
    total = min(len(entries), end) - start + 1
    total = max(0, min(total, Config.MAX_PLAYLIST_ITEMS))

    if total <= 0:
        await chat.send_message("❌ Invalid range.", parse_mode=ParseMode.HTML)
        return

    # Progress message
    progress_msg = await chat.send_message(
        f"📁 <b>Downloading Playlist</b>\n\n"
        f"📊 Range: {start}-{min(end, len(entries))}\n"
        f"🎵 Format: {format_detail.upper() if format_type == 'audio' else format_detail + 'p'}\n"
        f"📹 Total: {total} videos\n\n"
        f"⏳ Starting...",
        parse_mode=ParseMode.HTML,
    )

    completed = 0
    failed = 0

    for i in range(start - 1, min(end, len(entries))):
        entry = entries[i]
        entry_url = entry.get("url", "")
        entry_title = entry.get("title", f"Video {i+1}")

        if not entry_url:
            failed += 1
            continue

        # Update progress
        current = i - start + 2
        try:
            await progress_msg.edit_text(
                f"📁 <b>Downloading Playlist</b>\n\n"
                f"📥 [{current}/{total}] {Helpers.escape_html(entry_title[:50])}\n\n"
                f"{Messages.progress_bar(completed / total * 100)} "
                f"{round(completed / total * 100)}%\n\n"
                f"✅ Done: {completed} | ❌ Failed: {failed}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass

        # Download individual entry
        try:
            if format_type == "audio":
                file_path = await downloader.download_audio(
                    url=entry_url, user_id=user_id,
                    format=format_detail, bitrate=320,
                )
                if file_path and file_path.exists():
                    file_size = file_path.stat().st_size
                    if file_size <= Config.TELEGRAM_MAX_FILE_SIZE:
                        with open(file_path, "rb") as f:
                            await chat.send_audio(
                                audio=f,
                                filename=file_path.name,
                                caption=f"🎵 {Helpers.escape_html(entry_title[:200])}\n📁 [{current}/{total}]",
                                parse_mode=ParseMode.HTML,
                            )
                        completed += 1
                    else:
                        failed += 1
            else:
                file_path = await downloader.download_video(
                    url=entry_url, user_id=user_id,
                    resolution=format_detail, format="mp4",
                )
                if file_path and file_path.exists():
                    file_size = file_path.stat().st_size
                    max_size = Config.TELEGRAM_MAX_FILE_SIZE_LOCAL if Config.USE_LOCAL_API else Config.TELEGRAM_MAX_FILE_SIZE
                    if file_size <= max_size:
                        with open(file_path, "rb") as f:
                            await chat.send_video(
                                video=f,
                                filename=file_path.name,
                                caption=f"🎬 {Helpers.escape_html(entry_title[:200])}\n📁 [{current}/{total}]",
                                parse_mode=ParseMode.HTML,
                                supports_streaming=True,
                            )
                        completed += 1
                    else:
                        failed += 1

        except Exception as e:
            logger.error(f"Playlist item {i+1} error: {e}")
            failed += 1

        finally:
            file_manager.cleanup_user_files(user_id)

        # Small delay to avoid rate limits
        await asyncio.sleep(1)

    # Final summary
    await progress_msg.edit_text(
        f"🎉 <b>Playlist Download Complete!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Completed: <b>{completed}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total: <b>{total}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ @YTGrabDownBot",
        parse_mode=ParseMode.HTML,
    )

    # Update DB
    for _ in range(completed):
        await db.increment_downloads(user_id)

    logger.info(f"📁 Playlist done: {completed}/{total} for user {user_id}")


def _get_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Extract URL from command."""
    if context.args:
        return context.args[0]
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            url = Validators.extract_url(parts[1])
            if url:
                return url
    return None
