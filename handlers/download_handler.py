"""
YTGrab Bot - Download Handler
Core URL detection, media info display, and download execution.
"""

import re
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from loguru import logger

from config import Config
from models.database import db
from services.downloader import downloader, DownloadProgress
from utils.keyboards import Keyboards
from templates.messages import Messages


# ─── URL Detection Regex ────────────────────────────────────

URL_PATTERN = re.compile(
    r'(https?://(?:www\.)?'
    r'(?:youtube\.com/(?:watch\?v=|shorts/|live/|playlist\?list=|@[\w.-]+|channel/[\w.-]+)|'
    r'youtu\.be/[\w.-]+|'
    r'soundcloud\.com/[\w.-]+/[\w.-]+|'
    r'twitter\.com/\w+/status/\d+|'
    r'x\.com/\w+/status/\d+|'
    r'instagram\.com/(?:p|reel|tv)/[\w.-]+|'
    r'tiktok\.com/@[\w.-]+/video/\d+|'
    r'facebook\.com/(?:watch/\?v=|[\w.-]+/videos/)\d+|'
    r'vimeo\.com/\d+|'
    r'reddit\.com/r/\w+/comments/[\w.-]+|'
    r'dailymotion\.com/video/[\w.-]+|'
    r'twitch\.tv/(?:videos/\d+|[\w.-]+/clip/[\w.-]+)|'
    r'pinterest\.(?:com|co\.\w+)/pin/\d+'
    r')\S*)',
    re.IGNORECASE
)


def extract_url(text: str) -> str | None:
    """Extract a valid media URL from text."""
    if not text:
        return None
    match = URL_PATTERN.search(text)
    if match:
        return match.group(1).rstrip('.,;!?')
    # Fallback: any URL
    url_match = re.search(r'https?://\S+', text)
    if url_match:
        return url_match.group(0).rstrip('.,;!?')
    return None


# ─── Main URL Handler (auto-detect) ────────────────────────

async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message containing a URL."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    # Check if banned
    if await db.is_banned(user_id):
        await update.message.reply_text(
            Messages.ERROR_BANNED, parse_mode=ParseMode.HTML
        )
        return

    # Check rate limit
    downloads_today = await db.get_downloads_today(user_id)
    if downloads_today >= Config.RATE_LIMIT_PER_DAY:
        await update.message.reply_text(
            Messages.ERROR_RATE_LIMIT.format(
                wait_time="until tomorrow",
                limit=Config.RATE_LIMIT_PER_DAY,
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    # Extract URL
    url = extract_url(update.message.text)
    if not url:
        return  # Not a URL message, ignore

    logger.info(f"🔗 URL detected from user {user_id}: {url}")

    # Show detecting message
    detecting_msg = await update.message.reply_text(
        Messages.DETECTING_URL, parse_mode=ParseMode.HTML
    )

    # Show media info with action buttons
    await _show_media_info_from_message(detecting_msg, url)


# ─── Command Handlers ───────────────────────────────────────

async def mp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mp3 command - direct audio download."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "🎵 <b>Usage:</b> /mp3 <url>\n\n"
            "Example: /mp3 https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    # Get user preferences
    user_prefs = await db.get_user(user_id)
    bitrate = user_prefs.get("default_audio_bitrate", 320) if user_prefs else 320

    await _execute_audio_download(
        update=update,
        url=url,
        user_id=user_id,
        format="mp3",
        bitrate=bitrate,
    )


async def mp4_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mp4 command - direct video download."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "🎬 <b>Usage:</b> /mp4 <url>\n\n"
            "Example: /mp4 https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    # Get user preferences
    user_prefs = await db.get_user(user_id)
    resolution = user_prefs.get("default_video_resolution", "1080") if user_prefs else "1080"

    await _execute_video_download(
        update=update,
        url=url,
        user_id=user_id,
        resolution=resolution,
        format="mp4",
    )


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - show media information."""
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "📋 <b>Usage:</b> /info <url>\n\n"
            "Example: /info https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        Messages.DETECTING_URL, parse_mode=ParseMode.HTML
    )
    await _show_detailed_info_from_message(msg, url)


async def best_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /best command - download best quality."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "✨ <b>Usage:</b> /best <url>\n\n"
            "Example: /best https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    await _execute_video_download(
        update=update,
        url=url,
        user_id=user_id,
        resolution="best",
        format="mp4",
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command - search YouTube."""
    query_text = " ".join(context.args) if context.args else ""

    if not query_text:
        await update.message.reply_text(
            "🔍 <b>Usage:</b> /search <query>\n\n"
            "Example: /search lofi hip hop radio",
            parse_mode=ParseMode.HTML,
        )
        return

    await update.effective_chat.send_action(ChatAction.TYPING)

    # Use yt-dlp to search
    import yt_dlp

    def _search():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"ytsearch5:{query_text}", download=False)

    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _search)

        if not results or not results.get("entries"):
            await update.message.reply_text(
                f"🔍 No results found for: <b>{query_text}</b>\n\nTry different keywords.",
                parse_mode=ParseMode.HTML,
            )
            return

        # Format results
        text = f"🔍 <b>Search Results: \"{query_text}\"</b>\n\n"
        buttons = []

        for i, entry in enumerate(results.get("entries", [])[:5]):
            title = entry.get("title", "Unknown")[:45]
            duration = entry.get("duration", 0) or 0
            duration_str = _format_duration(duration)
            channel = entry.get("channel", entry.get("uploader", ""))[:25]
            url = entry.get("url", entry.get("webpage_url", ""))

            text += f"{i+1}. 🎵 <b>{title}</b>\n"
            text += f"   👤 {channel} | ⏱ {duration_str}\n\n"

            buttons.append([
                __import__('telegram').InlineKeyboardButton(
                    f"⬇️ {title[:35]}...",
                    callback_data=f"search_dl|{url}"
                )
            ])

        buttons.append([
            __import__('telegram').InlineKeyboardButton(
                "⬅️ Back", callback_data="back_start"
            )
        ])

        from telegram import InlineKeyboardMarkup
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(
            "❌ Search failed. Please try again.",
            parse_mode=ParseMode.HTML,
        )


# ─── Internal Helper Functions ──────────────────────────────

def _get_url_from_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Extract URL from command arguments or message text."""
    # From command args
    if context.args:
        url = " ".join(context.args)
        if url.startswith("http"):
            return url

    # From message text (after command)
    if update.message and update.message.text:
        text = update.message.text
        # Remove the command part
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            url = extract_url(parts[1])
            if url:
                return url

    return None


async def _show_media_info_from_message(msg, url: str):
    """Show media info by editing an existing message."""
    info = await downloader.extract_info(url)

    if info.error:
        error_text = _get_error_message(info.error)
        await msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        return

    if info.is_playlist:
        text = (
            f"📋 <b>Playlist: {info.title}</b>\n\n"
            f"📹 Videos: {info.playlist_count}\n\n"
            f"💡 Use /pl <url> to download playlist\n"
            f"💡 Or send individual video URLs"
        )
        await msg.edit_text(text, parse_mode=ParseMode.HTML)
        return

    text = Messages.VIDEO_INFO.format(
        title=_escape_html(info.title),
        uploader=_escape_html(info.uploader),
        duration=info.duration_str,
        views=Messages.format_number(info.views),
        likes=Messages.format_number(info.likes),
        platform=info.extractor.capitalize(),
    )

    await msg.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.media_action_menu(url),
        disable_web_page_preview=True,
    )


async def _show_media_info(query, url: str):
    """Show media info from callback query."""
    await query.edit_message_text(
        Messages.DETECTING_URL, parse_mode=ParseMode.HTML
    )
    info = await downloader.extract_info(url)

    if info.error:
        error_text = _get_error_message(info.error)
        await query.edit_message_text(
            error_text,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.error_retry(url),
        )
        return

    text = Messages.VIDEO_INFO.format(
        title=_escape_html(info.title),
        uploader=_escape_html(info.uploader),
        duration=info.duration_str,
        views=Messages.format_number(info.views),
        likes=Messages.format_number(info.likes),
        platform=info.extractor.capitalize(),
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=Keyboards.media_action_menu(url),
        disable_web_page_preview=True,
    )


async def _show_detailed_info(query, url: str):
    """Show detailed info from callback."""
    await query.edit_message_text(
        Messages.DETECTING_URL, parse_mode=ParseMode.HTML
    )
    await _show_detailed_info_from_message(query.message, url, query=query)


async def _show_detailed_info_from_message(msg, url: str, query=None):
    """Show detailed media information."""
    info = await downloader.extract_info(url)

    if info.error:
        error_text = _get_error_message(info.error)
        if query:
            await query.edit_message_text(error_text, parse_mode=ParseMode.HTML)
        else:
            await msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        return

    text = (
        f"📋 <b>Detailed Information</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 <b>Title:</b> {_escape_html(info.title)}\n"
        f"👤 <b>Uploader:</b> {_escape_html(info.uploader)}\n"
        f"⏱ <b>Duration:</b> {info.duration_str}\n"
        f"👁 <b>Views:</b> {Messages.format_number(info.views)}\n"
        f"👍 <b>Likes:</b> {Messages.format_number(info.likes)}\n"
        f"🌐 <b>Platform:</b> {info.extractor}\n"
        f"🔗 <b>URL:</b> {url}\n"
    )

    if info.is_live:
        text += f"🔴 <b>Status:</b> LIVE\n"

    if info.subtitles:
        text += f"📝 <b>Subtitles:</b> {', '.join(info.subtitles[:10])}\n"

    if info.formats:
        text += f"\n📺 <b>Available Qualities:</b>\n"
        for fmt in info.formats[:8]:
            size_str = Messages.format_filesize(fmt['filesize']) if fmt['filesize'] else "?"
            text += f"  • {fmt['resolution']} ({fmt['ext']}) - {size_str}\n"

    if info.description:
        desc = info.description[:300] + "..." if len(info.description) > 300 else info.description
        text += f"\n📄 <b>Description:</b>\n{_escape_html(desc)}\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━━"

    if query:
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.media_action_menu(url),
            disable_web_page_preview=True,
        )
    else:
        await msg.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.media_action_menu(url),
            disable_web_page_preview=True,
        )


# ─── Download Execution ─────────────────────────────────────

async def _handle_audio_download(query, data: str, user_id: int):
    """Handle audio download from callback."""
    # Parse: dl_mp3_320|url
    parts = data.split("|", 1)
    format_info = parts[0]  # dl_mp3_320
    url = parts[1]

    # Extract format and bitrate
    segments = format_info.split("_")  # ['dl', 'mp3', '320']
    format = segments[1]
    bitrate = int(segments[2]) if len(segments) > 2 else 320

    await query.edit_message_text(
        f"⬇️ <b>Downloading Audio...</b>\n\n"
        f"🎵 Format: {format.upper()} | {bitrate}kbps\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    await _execute_audio_download(
        update=query,
        url=url,
        user_id=user_id,
        format=format,
        bitrate=bitrate,
        is_callback=True,
    )


async def _handle_video_download(query, data: str, user_id: int):
    """Handle video download from callback."""
    # Parse: dl_vid_1080|url
    parts = data.split("|", 1)
    format_info = parts[0]  # dl_vid_1080
    url = parts[1]

    resolution = format_info.replace("dl_vid_", "")

    await query.edit_message_text(
        f"⬇️ <b>Downloading Video...</b>\n\n"
        f"📺 Quality: {resolution}p | Format: MP4\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    await _execute_video_download(
        update=query,
        url=url,
        user_id=user_id,
        resolution=resolution,
        format="mp4",
        is_callback=True,
    )


async def _handle_subtitle_download(query, data: str, user_id: int):
    """Handle subtitle download from callback."""
    # Parse: dl_sub_en|url
    parts = data.split("|", 1)
    lang = parts[0].replace("dl_sub_", "")
    url = parts[1]

    await query.edit_message_text(
        f"📝 <b>Downloading Subtitles...</b>\n\n"
        f"🌐 Language: {lang.upper()}\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        file_path = await downloader.download_subtitles(url, user_id, lang=lang)

        if file_path and file_path.exists():
            with open(file_path, "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename=file_path.name,
                    caption=f"📝 Subtitles ({lang.upper()})",
                )
            downloader.cleanup_user_files(user_id)
            await query.edit_message_text(
                "✅ <b>Subtitles downloaded!</b>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.edit_message_text(
                f"❌ No subtitles found for language: {lang.upper()}\n\n"
                f"Try a different language.",
                parse_mode=ParseMode.HTML,
                reply_markup=Keyboards.subtitle_lang_menu(url),
            )
    except Exception as e:
        logger.error(f"Subtitle download error: {e}")
        await query.edit_message_text(
            Messages.ERROR_DOWNLOAD_FAILED,
            parse_mode=ParseMode.HTML,
        )


async def _download_thumbnail(query, url: str, user_id: int):
    """Download and send thumbnail."""
    await query.edit_message_text(
        "🖼 <b>Downloading Thumbnail...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        file_path = await downloader.download_thumbnail(url, user_id)

        if file_path and file_path.exists():
            with open(file_path, "rb") as f:
                await query.message.reply_photo(
                    photo=f,
                    caption="🖼 <b>Thumbnail</b>",
                    parse_mode=ParseMode.HTML,
                )
            downloader.cleanup_user_files(user_id)
            await query.edit_message_text(
                "✅ <b>Thumbnail sent!</b>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.edit_message_text(
                "❌ No thumbnail available for this video.",
                parse_mode=ParseMode.HTML,
            )
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        await query.edit_message_text(
            "❌ Failed to download thumbnail.",
            parse_mode=ParseMode.HTML,
        )


async def _execute_audio_download(
    update, url: str, user_id: int,
    format: str = "mp3", bitrate: int = 320,
    is_callback: bool = False,
):
    """Execute audio download and send file."""
    chat_id = update.effective_chat.id if hasattr(update, 'effective_chat') else update.message.chat_id

    # Progress message
    if is_callback:
        progress_msg = await update.message.reply_text(
            "⬇️ <b>Downloading Audio...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )
    else:
        progress_msg = await update.message.reply_text(
            "⬇️ <b>Downloading Audio...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )

    last_update_time = [0]

    async def progress_callback(progress: DownloadProgress):
        """Update progress message (throttled)."""
        import time
        now = time.time()
        if now - last_update_time[0] < 3:  # Update every 3 seconds
            return
        last_update_time[0] = now

        bar = Messages.progress_bar(progress.percent)
        size_str = Messages.format_filesize(progress.total_bytes)

        text = (
            f"⬇️ <b>Downloading Audio...</b>\n\n"
            f"🎵 Format: {format.upper()} | {bitrate}kbps\n\n"
            f"{bar} {progress.percent}%\n"
            f"⚡ Speed: {progress.speed}\n"
            f"⏱ ETA: {progress.eta}\n"
            f"📦 Size: {size_str}"
        )
        try:
            await progress_msg.edit_text(text, parse_mode=ParseMode.HTML)
        except Exception:
            pass

    try:
        # Send typing action
        await update.effective_chat.send_action(ChatAction.UPLOAD_AUDIO)

        # Download
        file_path = await downloader.download_audio(
            url=url,
            user_id=user_id,
            format=format,
            bitrate=bitrate,
            progress_callback=progress_callback,
        )

        if not file_path or not file_path.exists():
            await progress_msg.edit_text(
                Messages.ERROR_DOWNLOAD_FAILED,
                parse_mode=ParseMode.HTML,
                reply_markup=Keyboards.error_retry(url),
            )
            return

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > Config.TELEGRAM_MAX_FILE_SIZE and not Config.USE_LOCAL_API:
            await progress_msg.edit_text(
                Messages.ERROR_FILE_TOO_LARGE.format(
                    size=Messages.format_filesize(file_size),
                    limit="50MB",
                ),
                parse_mode=ParseMode.HTML,
            )
            downloader.cleanup_user_files(user_id)
            return

        # Send file
        await progress_msg.edit_text(
            "📤 <b>Uploading to Telegram...</b>",
            parse_mode=ParseMode.HTML,
        )

        with open(file_path, "rb") as f:
            await update.effective_chat.send_audio(
                audio=f,
                filename=file_path.name,
                caption=(
                    f"🎵 <b>{_escape_html(file_path.stem)}</b>\n"
                    f"📦 {Messages.format_filesize(file_size)} | "
                    f"🎧 {format.upper()} {bitrate}kbps\n\n"
                    f"⚡ @YTGrabDownBot"
                ),
                parse_mode=ParseMode.HTML,
            )

        # Update database
        await db.increment_downloads(user_id)
        await db.add_download_history(
            user_id=user_id,
            url=url,
            title=file_path.stem,
            format=format,
            file_size=file_size,
        )

        # Cleanup
        downloader.cleanup_user_files(user_id)

        # Final message
        await progress_msg.edit_text(
            Messages.DOWNLOAD_COMPLETE.format(
                title=_escape_html(file_path.stem),
                size=Messages.format_filesize(file_size),
                duration="N/A",
            ),
            parse_mode=ParseMode.HTML,
        )

        logger.info(f"✅ Audio sent: {file_path.name} ({Messages.format_filesize(file_size)})")

    except Exception as e:
        logger.error(f"Audio download error: {e}")
        downloader.cleanup_user_files(user_id)
        await progress_msg.edit_text(
            Messages.ERROR_DOWNLOAD_FAILED,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.error_retry(url),
        )


async def _execute_video_download(
    update, url: str, user_id: int,
    resolution: str = "1080", format: str = "mp4",
    is_callback: bool = False,
):
    """Execute video download and send file."""
    # Progress message
    if is_callback:
        progress_msg = await update.message.reply_text(
            "⬇️ <b>Downloading Video...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )
    else:
        progress_msg = await update.message.reply_text(
            "⬇️ <b>Downloading Video...</b>\n\n⏳ Starting...",
            parse_mode=ParseMode.HTML,
        )

    last_update_time = [0]

    async def progress_callback(progress: DownloadProgress):
        """Update progress message (throttled)."""
        import time
        now = time.time()
        if now - last_update_time[0] < 3:
            return
        last_update_time[0] = now

        bar = Messages.progress_bar(progress.percent)
        size_str = Messages.format_filesize(progress.total_bytes)

        text = (
            f"⬇️ <b>Downloading Video...</b>\n\n"
            f"📺 Quality: {resolution} | Format: {format.upper()}\n\n"
            f"{bar} {progress.percent}%\n"
            f"⚡ Speed: {progress.speed}\n"
            f"⏱ ETA: {progress.eta}\n"
            f"📦 Size: {size_str}"
        )
        try:
            await progress_msg.edit_text(text, parse_mode=ParseMode.HTML)
        except Exception:
            pass

    try:
        # Send typing action
        await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)

        # Download
        file_path = await downloader.download_video(
            url=url,
            user_id=user_id,
            resolution=resolution,
            format=format,
            progress_callback=progress_callback,
        )

        if not file_path or not file_path.exists():
            await progress_msg.edit_text(
                Messages.ERROR_DOWNLOAD_FAILED,
                parse_mode=ParseMode.HTML,
                reply_markup=Keyboards.error_retry(url),
            )
            return

        # Check file size
        file_size = file_path.stat().st_size
        max_size = Config.TELEGRAM_MAX_FILE_SIZE_LOCAL if Config.USE_LOCAL_API else Config.TELEGRAM_MAX_FILE_SIZE

        if file_size > max_size:
            await progress_msg.edit_text(
                Messages.ERROR_FILE_TOO_LARGE.format(
                    size=Messages.format_filesize(file_size),
                    limit=Messages.format_filesize(max_size),
                ),
                parse_mode=ParseMode.HTML,
            )
            downloader.cleanup_user_files(user_id)
            return

        # Send file
        await progress_msg.edit_text(
            "📤 <b>Uploading to Telegram...</b>\n⏳ This may take a moment for large files.",
            parse_mode=ParseMode.HTML,
        )

        with open(file_path, "rb") as f:
            await update.effective_chat.send_video(
                video=f,
                filename=file_path.name,
                caption=(
                    f"🎬 <b>{_escape_html(file_path.stem)}</b>\n"
                    f"📦 {Messages.format_filesize(file_size)} | "
                    f"📺 {resolution}p {format.upper()}\n\n"
                    f"⚡ @YTGrabDownBot"
                ),
                parse_mode=ParseMode.HTML,
                supports_streaming=True,
            )

        # Update database
        await db.increment_downloads(user_id)
        await db.add_download_history(
            user_id=user_id,
            url=url,
            title=file_path.stem,
            format=f"{format}_{resolution}p",
            file_size=file_size,
        )

        # Cleanup
        downloader.cleanup_user_files(user_id)

        # Final message
        await progress_msg.edit_text(
            Messages.DOWNLOAD_COMPLETE.format(
                title=_escape_html(file_path.stem),
                size=Messages.format_filesize(file_size),
                duration="N/A",
            ),
            parse_mode=ParseMode.HTML,
        )

        logger.info(f"✅ Video sent: {file_path.name} ({Messages.format_filesize(file_size)})")

    except Exception as e:
        logger.error(f"Video download error: {e}")
        downloader.cleanup_user_files(user_id)
        await progress_msg.edit_text(
            Messages.ERROR_DOWNLOAD_FAILED,
            parse_mode=ParseMode.HTML,
            reply_markup=Keyboards.error_retry(url),
        )


# ─── Utility Functions ──────────────────────────────────────

def _get_error_message(error: str) -> str:
    """Map error code to user-friendly message."""
    error_map = {
        "private": Messages.ERROR_PRIVATE,
        "age_restricted": Messages.ERROR_AGE_RESTRICTED,
        "not_found": Messages.ERROR_NOT_FOUND,
        "copyright": Messages.ERROR_COPYRIGHT,
    }
    if error in error_map:
        return error_map[error]
    return Messages.ERROR_DOWNLOAD_FAILED


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _format_duration(seconds: int) -> str:
    """Format seconds to readable duration."""
    if not seconds:
        return "0:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
