"""
YTGrab Bot - Video Handler
Video format commands: /webm, /mkv, /gif, /clip, /noaudio, /worst
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from loguru import logger

from config import Config
from models.database import db
from services.downloader import downloader
from services.file_manager import file_manager
from utils.helpers import Helpers
from utils.validators import Validators
from handlers.download_handler import _execute_video_download, _get_url_from_command


async def webm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /webm command."""
    await _video_format_command(update, context, "webm")

async def mkv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mkv command."""
    await _video_format_command(update, context, "mkv")


async def worst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /worst command - smallest file size."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "💾 <b>Usage:</b> /worst <url>\n\nDownloads lowest quality (saves data)",
            parse_mode=ParseMode.HTML,
        )
        return

    await _execute_video_download(
        update=update, url=url, user_id=user_id,
        resolution="worst", format="mp4",
    )


async def gif_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gif command - convert video to GIF."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "🎞️ <b>Usage:</b> /gif <url>\n\n"
            "Converts first 10 seconds to GIF.\n"
            "For specific range: /gif <url> 01:20 (start time)",
            parse_mode=ParseMode.HTML,
        )
        return

    # Optional start time
    start_time = "0"
    if context.args and len(context.args) > 1:
        start_time = context.args[1]

    msg = await update.message.reply_text(
        "🎞️ <b>Creating GIF...</b>\n\n⏳ Downloading & converting...",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_DOCUMENT)

        # Download video first (low quality for GIF)
        file_path = await downloader.download_video(
            url=url, user_id=user_id,
            resolution="360", format="mp4",
        )

        if not file_path or not file_path.exists():
            await msg.edit_text("❌ Failed to download video for GIF.", parse_mode=ParseMode.HTML)
            return

        # Convert to GIF
        gif_path = await file_manager.convert_to_gif(
            video_path=file_path,
            start_time=start_time,
            duration=Config.MAX_GIF_DURATION,
            width=Config.GIF_WIDTH,
            fps=Config.GIF_FPS,
        )

        if gif_path and gif_path.exists():
            gif_size = gif_path.stat().st_size
            if gif_size <= Config.TELEGRAM_MAX_FILE_SIZE:
                with open(gif_path, "rb") as f:
                    await update.effective_chat.send_animation(
                        animation=f,
                        caption=(
                            f"🎞️ <b>GIF</b>\n"
                            f"📦 {Helpers.format_filesize(gif_size)}\n"
                            f"⏱ {Config.MAX_GIF_DURATION}s | {Config.GIF_WIDTH}px\n\n"
                            f"⚡ @YTGrabDownBot"
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                await msg.edit_text("✅ <b>GIF created & sent!</b>", parse_mode=ParseMode.HTML)
            else:
                await msg.edit_text(
                    f"⚠️ GIF too large ({Helpers.format_filesize(gif_size)}). "
                    f"Max: {Helpers.format_filesize(Config.TELEGRAM_MAX_FILE_SIZE)}",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await msg.edit_text("❌ GIF conversion failed.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"GIF error: {e}")
        await msg.edit_text("❌ GIF creation failed.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def clip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clip command - download specific time range."""
    user_id = update.effective_user.id

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "✂️ <b>Usage:</b> /clip <url> <start-end>\n\n"
            "Examples:\n"
            "  /clip <url> 01:20-02:45\n"
            "  /clip <url> 80-165\n"
            "  /clip <url> 0:30-1:00",
            parse_mode=ParseMode.HTML,
        )
        return

    url = context.args[0]
    time_range = " ".join(context.args[1:])
    start_time, end_time = Validators.parse_time_range(time_range)

    if not start_time or not end_time:
        await update.message.reply_text(
            "❌ Invalid time range.\n\n"
            "Use format: <code>MM:SS-MM:SS</code> or <code>seconds-seconds</code>\n"
            "Example: /clip <url> 01:20-02:45",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        f"✂️ <b>Clipping Video...</b>\n\n"
        f"⏱ Range: {start_time} → {end_time}\n"
        f"⏳ Downloading & trimming...",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)

        # Download with time range using yt-dlp
        import yt_dlp
        from pathlib import Path

        output_dir = Config.DOWNLOADS_DIR / str(user_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(output_dir / "%(title).200s_clip.%(ext)s")

        opts = {
            **Config.YTDLP_OPTIONS,
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "outtmpl": output_template,
            "download_ranges": None,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                },
            ],
            "external_downloader_args": {
                "ffmpeg_i": ["-ss", start_time, "-to", end_time],
            },
            "merge_output_format": "mp4",
        }

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download)

        # Find clip file
        clip_file = None
        for f in output_dir.iterdir():
            if "_clip" in f.name and f.suffix == ".mp4":
                clip_file = f
                break

        if clip_file and clip_file.exists():
            file_size = clip_file.stat().st_size
            max_size = Config.TELEGRAM_MAX_FILE_SIZE_LOCAL if Config.USE_LOCAL_API else Config.TELEGRAM_MAX_FILE_SIZE

            if file_size <= max_size:
                with open(clip_file, "rb") as f:
                    await update.effective_chat.send_video(
                        video=f,
                        filename=clip_file.name,
                        caption=(
                            f"✂️ <b>Video Clip</b>\n"
                            f"⏱ {start_time} → {end_time}\n"
                            f"📦 {Helpers.format_filesize(file_size)}\n\n"
                            f"⚡ @YTGrabDownBot"
                        ),
                        parse_mode=ParseMode.HTML,
                        supports_streaming=True,
                    )
                await msg.edit_text("✅ <b>Clip downloaded & sent!</b>", parse_mode=ParseMode.HTML)
            else:
                await msg.edit_text(
                    f"⚠️ Clip too large ({Helpers.format_filesize(file_size)}). Try a shorter range.",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await msg.edit_text("❌ Clip creation failed.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Clip error: {e}")
        await msg.edit_text("❌ Clip failed. Try different time range.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def noaudio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /noaudio command - video without audio track."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            "🔇 <b>Usage:</b> /noaudio <url>\n\nDownloads video without audio track.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "🔇 <b>Downloading Video (No Audio)...</b>\n\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        import yt_dlp
        from pathlib import Path

        output_dir = Config.DOWNLOADS_DIR / str(user_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(output_dir / "%(title).200s_noaudio.%(ext)s")

        opts = {
            **Config.YTDLP_OPTIONS,
            "format": "bestvideo[height<=1080]/bestvideo",
            "outtmpl": output_template,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
            ],
        }

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download)

        vid_file = None
        for f in output_dir.iterdir():
            if "_noaudio" in f.name:
                vid_file = f
                break

        if vid_file and vid_file.exists():
            file_size = vid_file.stat().st_size
            with open(vid_file, "rb") as f:
                await update.effective_chat.send_video(
                    video=f,
                    filename=vid_file.name,
                    caption=f"🔇 <b>Video (No Audio)</b>\n📦 {Helpers.format_filesize(file_size)}\n\n⚡ @YTGrabDownBot",
                    parse_mode=ParseMode.HTML,
                    supports_streaming=True,
                )
            await msg.edit_text("✅ <b>Video (no audio) sent!</b>", parse_mode=ParseMode.HTML)
        else:
            await msg.edit_text("❌ Download failed.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"No-audio error: {e}")
        await msg.edit_text("❌ Download failed.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def _video_format_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE, format: str
):
    """Generic video format command."""
    user_id = update.effective_user.id
    url = _get_url_from_command(update, context)

    if not url:
        await update.message.reply_text(
            f"🎬 <b>Usage:</b> /{format} <url>\n\n"
            f"Example: /{format} https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    user_prefs = await db.get_user(user_id)
    resolution = user_prefs.get("default_video_resolution", "1080") if user_prefs else "1080"

    await _execute_video_download(
        update=update, url=url, user_id=user_id,
        resolution=resolution, format=format,
    )
