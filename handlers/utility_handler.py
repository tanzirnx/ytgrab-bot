"""
YTGrab Bot - Utility Handler
Commands: /queue, /cancel, /clearqueue, /trending, /shorts, /batch, /report, /feedback, /suggest
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from loguru import logger

from config import Config
from models.database import db
from services.queue_manager import queue_manager
from services.downloader import downloader
from utils.helpers import Helpers
from utils.validators import Validators

import yt_dlp


async def queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /queue command - show download queue."""
    user_id = update.effective_user.id
    status = await queue_manager.get_queue_status(user_id)

    if not status["queued"] and not status["active"]:
        await update.message.reply_text(
            "📊 <b>Your Queue is Empty</b>\n\n"
            "No active or queued downloads.\n"
            "Paste a URL to start downloading!",
            parse_mode=ParseMode.HTML,
        )
        return

    text = "📊 <b>Download Queue</b>\n\n"

    if status["active"]:
        text += "🔄 <b>Active:</b>\n"
        for task in status["active"]:
            text += f"  ⬇️ #{task['id']}: {Helpers.escape_html(task['title'][:40])} ({task['progress']}%)\n"
        text += "\n"

    if status["queued"]:
        text += "⏳ <b>Queued:</b>\n"
        for task in status["queued"]:
            text += f"  📋 #{task['id']}: {Helpers.escape_html(task['title'][:40])}\n"
        text += "\n"

    text += f"📊 {status['total_active']} active | {status['total_queued']} queued | Max: {status['max_queue']}"

    buttons = [
        [InlineKeyboardButton("🚫 Cancel All", callback_data="queue_cancel_all")],
    ]

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command."""
    user_id = update.effective_user.id

    if context.args:
        try:
            task_id = int(context.args[0])
            success = await queue_manager.cancel_task(user_id, task_id)
            if success:
                await update.message.reply_text(f"🚫 Task #{task_id} cancelled.")
            else:
                await update.message.reply_text(f"❌ Task #{task_id} not found in your queue.")
        except ValueError:
            await update.message.reply_text("❌ Invalid task ID. Use: /cancel <task_id>")
    else:
        count = await queue_manager.cancel_all(user_id)
        await update.message.reply_text(f"🚫 Cancelled <b>{count}</b> tasks.", parse_mode=ParseMode.HTML)


async def clearqueue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clearqueue command."""
    user_id = update.effective_user.id
    count = await queue_manager.cancel_all(user_id)
    await update.message.reply_text(
        f"🧹 Queue cleared! Removed <b>{count}</b> tasks.",
        parse_mode=ParseMode.HTML,
    )


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trending command."""
    region = context.args[0].upper() if context.args else "US"

    msg = await update.message.reply_text(
        f"🔥 <i>Fetching trending videos ({region})...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        def _fetch():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "skip_download": True,
                "geo_bypass_country": region,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info("https://www.youtube.com/feed/trending", download=False)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _fetch)

        if not data or not data.get("entries"):
            await msg.edit_text("❌ Could not fetch trending videos.")
            return

        entries = data.get("entries", [])[:10]
        text = f"🔥 <b>Trending in {region}</b>\n\n"
        buttons = []

        for i, entry in enumerate(entries):
            title = Helpers.escape_html(entry.get("title", "Unknown")[:45])
            channel = Helpers.escape_html(entry.get("channel", entry.get("uploader", ""))[:25])
            url = entry.get("url", entry.get("webpage_url", ""))
            duration = Helpers.format_duration(entry.get("duration", 0))

            text += f"{i+1}. 🎬 <b>{title}</b>\n   👤 {channel} | ⏱ {duration}\n\n"
            buttons.append([
                InlineKeyboardButton(
                    f"⬇️ {title[:35]}...",
                    callback_data=f"search_dl|{url}"
                )
            ])

        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_start")])

        await msg.edit_text(
            Helpers.truncate(text, 3500),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Trending error: {e}")
        await msg.edit_text("❌ Failed to fetch trending videos.")


async def shorts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shorts command - download YouTube Shorts."""
    user_id = update.effective_user.id
    url = None

    if context.args:
        url = context.args[0]
    elif update.message and update.message.text:
        url = Validators.extract_url(update.message.text)

    if not url:
        await update.message.reply_text(
            "📱 <b>Usage:</b> /shorts <shorts_url>\n\n"
            "Example: /shorts https://youtube.com/shorts/xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    # Convert shorts URL to regular if needed
    url = url.replace("/shorts/", "/watch?v=")

    msg = await update.message.reply_text(
        "📱 <b>Downloading Short...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        file_path = await downloader.download_video(
            url=url, user_id=user_id,
            resolution="1080", format="mp4",
        )

        if file_path and file_path.exists():
            file_size = file_path.stat().st_size
            with open(file_path, "rb") as f:
                await update.effective_chat.send_video(
                    video=f,
                    filename=file_path.name,
                    caption=f"📱 <b>YouTube Short</b>\n📦 {Helpers.format_filesize(file_size)}\n\n⚡ @YTGrabDownBot",
                    parse_mode=ParseMode.HTML,
                    supports_streaming=True,
                )
            await msg.edit_text("✅ <b>Short downloaded!</b>", parse_mode=ParseMode.HTML)
            await db.increment_downloads(user_id)
        else:
            await msg.edit_text("❌ Download failed.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Shorts error: {e}")
        await msg.edit_text("❌ Download failed.", parse_mode=ParseMode.HTML)
    finally:
        from services.file_manager import file_manager
        file_manager.cleanup_user_files(user_id)


async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /batch command - download multiple URLs."""
    user_id = update.effective_user.id

    if not update.message.text:
        await update.message.reply_text(
            "📦 <b>Usage:</b> /batch <url1> <url2> <url3>...\n\n"
            "Or send URLs on separate lines:\n"
            "/batch\nurl1\nurl2\nurl3",
            parse_mode=ParseMode.HTML,
        )
        return

    # Extract all URLs
    text = update.message.text.replace("/batch", "").strip()
    urls = Validators.extract_all_urls(text)

    if not urls:
        await update.message.reply_text("❌ No valid URLs found in your message.")
        return

    if len(urls) > Config.MAX_BATCH_URLS:
        await update.message.reply_text(
            f"⚠️ Too many URLs ({len(urls)}). Max: {Config.MAX_BATCH_URLS}",
        )
        urls = urls[:Config.MAX_BATCH_URLS]

    msg = await update.message.reply_text(
        f"📦 <b>Batch Download</b>\n\n"
        f"📊 URLs: {len(urls)}\n"
        f"⏳ Starting...",
        parse_mode=ParseMode.HTML,
    )

    completed = 0
    failed = 0

    for i, url in enumerate(urls):
        try:
            await msg.edit_text(
                f"📦 <b>Batch Download</b>\n\n"
                f"📥 [{i+1}/{len(urls)}] Processing...\n"
                f"✅ Done: {completed} | ❌ Failed: {failed}",
                parse_mode=ParseMode.HTML,
            )

            # Default: download as MP3
            file_path = await downloader.download_audio(
                url=url, user_id=user_id, format="mp3", bitrate=320,
            )

            if file_path and file_path.exists():
                file_size = file_path.stat().st_size
                if file_size <= Config.TELEGRAM_MAX_FILE_SIZE:
                    with open(file_path, "rb") as f:
                        await update.effective_chat.send_audio(
                            audio=f,
                            filename=file_path.name,
                            caption=f"🎵 [{i+1}/{len(urls)}] {Helpers.escape_html(file_path.stem[:100])}",
                            parse_mode=ParseMode.HTML,
                        )
                    completed += 1
                    await db.increment_downloads(user_id)
                else:
                    failed += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"Batch item {i+1} error: {e}")
            failed += 1
        finally:
            from services.file_manager import file_manager
            file_manager.cleanup_user_files(user_id)

        await asyncio.sleep(1)

    await msg.edit_text(
        f"📦 <b>Batch Complete!</b>\n\n"
        f"✅ Completed: <b>{completed}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total: <b>{len(urls)}</b>",
        parse_mode=ParseMode.HTML,
    )


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command - report bug to admin."""
    user = update.effective_user
    message = " ".join(context.args) if context.args else "No details provided"

    report_text = (
        f"🐛 <b>Bug Report</b>\n\n"
        f"👤 From: {Helpers.escape_html(user.first_name)} (@{user.username or 'N/A'})\n"
        f"🆔 User ID: {user.id}\n"
        f"📝 Report: {Helpers.escape_html(message)}"
    )

    # Send to admin
    try:
        await context.bot.send_message(
            chat_id=Config.ADMIN_ID,
            text=report_text,
            parse_mode=ParseMode.HTML,
        )
        await update.message.reply_text(
            "✅ <b>Report sent!</b> Thank you for helping improve the bot.",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        await update.message.reply_text("❌ Could not send report. Try again later.")


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /feedback command."""
    user = update.effective_user
    message = " ".join(context.args) if context.args else ""

    if not message:
        await update.message.reply_text(
            "💬 <b>Usage:</b> /feedback <your message>\n\n"
            "Example: /feedback Great bot! Please add Spotify support.",
            parse_mode=ParseMode.HTML,
        )
        return

    feedback_text = (
        f"💬 <b>Feedback</b>\n\n"
        f"👤 From: {Helpers.escape_html(user.first_name)} (@{user.username or 'N/A'})\n"
        f"🆔 User ID: {user.id}\n"
        f"📝 Message: {Helpers.escape_html(message)}"
    )

    try:
        await context.bot.send_message(
            chat_id=Config.ADMIN_ID,
            text=feedback_text,
            parse_mode=ParseMode.HTML,
        )
        await update.message.reply_text(
            "✅ <b>Thank you for your feedback!</b> 💙",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        await update.message.reply_text("❌ Could not send feedback.")


async def suggest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /suggest command."""
    await feedback_command(update, context)  # Same as feedback
