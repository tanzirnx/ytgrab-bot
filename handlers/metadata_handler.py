"""
YTGrab Bot - Metadata Handler (Phase 3)
Commands: /thumb, /metadata, /description, /comments
"""

import json
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from loguru import logger

from config import Config
from services.downloader import downloader
from services.file_manager import file_manager
from services.metadata_service import metadata_service
from utils.helpers import Helpers
from utils.validators import Validators


async def thumb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /thumb or /thumbnail command."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "🖼 <b>Usage:</b> /thumb <url>\n\n"
            "Downloads the video thumbnail in best quality.\n"
            "Example: /thumb https://youtube.com/watch?v=xyz",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "🖼 <b>Downloading Thumbnail...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)

        file_path = await downloader.download_thumbnail(url, user_id)

        if file_path and file_path.exists():
            file_size = file_path.stat().st_size
            with open(file_path, "rb") as f:
                await update.effective_chat.send_photo(
                    photo=f,
                    caption=(
                        f"🖼 <b>Thumbnail</b>\n"
                        f"📦 {Helpers.format_filesize(file_size)}\n"
                        f"📄 {file_path.suffix.upper()}\n\n"
                        f"⚡ @YTGrabDownBot"
                    ),
                    parse_mode=ParseMode.HTML,
                )
            await msg.edit_text("✅ <b>Thumbnail sent!</b>", parse_mode=ParseMode.HTML)
        else:
            await msg.edit_text("❌ No thumbnail available for this video.", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Thumb error: {e}")
        await msg.edit_text("❌ Failed to download thumbnail.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def metadata_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /metadata command - download metadata as JSON."""
    user_id = update.effective_user.id
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📄 <b>Usage:</b> /metadata <url>\n\n"
            "Downloads full video metadata as JSON file.",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text(
        "📄 <b>Extracting Metadata...</b>\n⏳ Please wait...",
        parse_mode=ParseMode.HTML,
    )

    try:
        await update.effective_chat.send_action(ChatAction.UPLOAD_DOCUMENT)

        metadata = await metadata_service.extract_full_metadata(url)

        if not metadata:
            await msg.edit_text("❌ Could not extract metadata.", parse_mode=ParseMode.HTML)
            return

        # Save as JSON file
        user_dir = file_manager.get_user_dir(user_id)
        title = Helpers.sanitize_filename(metadata.get("title", "video")[:100])
        json_path = user_dir / f"{title}_metadata.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

        file_size = json_path.stat().st_size
        with open(json_path, "rb") as f:
            await update.effective_chat.send_document(
                document=f,
                filename=json_path.name,
                caption=(
                    f"📄 <b>Metadata JSON</b>\n"
                    f"🎬 {Helpers.escape_html(metadata.get('title', 'Unknown')[:100])}\n"
                    f"📦 {Helpers.format_filesize(file_size)}\n\n"
                    f"⚡ @YTGrabDownBot"
                ),
                parse_mode=ParseMode.HTML,
            )

        await msg.edit_text("✅ <b>Metadata exported!</b>", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Metadata error: {e}")
        await msg.edit_text("❌ Failed to extract metadata.", parse_mode=ParseMode.HTML)
    finally:
        file_manager.cleanup_user_files(user_id)


async def description_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /description command - get video description."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "📄 <b>Usage:</b> /description <url>",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = await update.message.reply_text("📄 <i>Fetching description...</i>", parse_mode=ParseMode.HTML)

    try:
        info = await downloader.extract_info(url)

        if info.error:
            await msg.edit_text("❌ Could not fetch video info.", parse_mode=ParseMode.HTML)
            return

        title = Helpers.escape_html(info.title)
        description = info.description or "No description available."

        text = (
            f"📄 <b>Description</b>\n\n"
            f"🎬 <b>{title}</b>\n"
            f"👤 {Helpers.escape_html(info.uploader)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{Helpers.escape_html(description)}"
        )

        await msg.edit_text(
            Helpers.truncate(text, 4000),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Description error: {e}")
        await msg.edit_text("❌ Failed to fetch description.", parse_mode=ParseMode.HTML)


async def comments_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /comments command - get top comments."""
    url = _get_url(update, context)

    if not url:
        await update.message.reply_text(
            "💬 <b>Usage:</b> /comments <url> [count]\n\n"
            "Gets top comments. Default: 10 comments.\n"
            "Example: /comments <url> 20",
            parse_mode=ParseMode.HTML,
        )
        return

    count = 10
    if context.args and len(context.args) > 1:
        try:
            count = min(int(context.args[1]), 50)
        except ValueError:
            pass

    msg = await update.message.reply_text(
        f"💬 <i>Fetching top {count} comments...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        comments = await metadata_service.get_comments(url, max_comments=count)

        if not comments:
            await msg.edit_text(
                "💬 <b>No comments found.</b>\n\n"
                "Comments may be disabled for this video.",
                parse_mode=ParseMode.HTML,
            )
            return

        info = await downloader.extract_info(url)
        title = Helpers.escape_html(info.title[:60]) if not info.error else "Video"

        text = f"💬 <b>Top Comments: {title}</b>\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, comment in enumerate(comments):
            author = Helpers.escape_html(comment.get("author", "Unknown")[:30])
            text_content = Helpers.escape_html(comment.get("text", "")[:200])
            likes = comment.get("like_count", 0)
            text += f"<b>{i+1}. {author}</b> (👍 {Helpers.format_number(likes)})\n"
            text += f"{text_content}\n\n"

        await msg.edit_text(
            Helpers.truncate(text, 4000),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Comments error: {e}")
        await msg.edit_text("❌ Failed to fetch comments.", parse_mode=ParseMode.HTML)


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
