"""
YTGrab Bot - Admin Handler
Admin commands: /admin, /stats, /broadcast, /ban, /unban, /setlimit, /maintenance, /logs, /update, /restart
"""

import sys
import asyncio
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from loguru import logger

from config import Config
from models.database import db
from services.queue_manager import queue_manager
from services.file_manager import file_manager
from utils.helpers import Helpers


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == Config.ADMIN_ID


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - admin dashboard."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    stats = await db.get_stats()
    queue_stats = await queue_manager.get_global_stats()
    storage = file_manager.get_storage_stats()
    uptime = Helpers.format_uptime(context.bot_data.get("start_time", 0))

    text = (
        f"📊 <b>YTGrab Bot Dashboard</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"📥 Downloads Today: <b>{stats['downloads_today']}</b>\n"
        f"📥 Downloads Total: <b>{stats['total_downloads']}</b>\n"
        f"💾 Total Data: <b>{stats['total_data_mb']} MB</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Queue Active: <b>{queue_stats['total_active']}/{Config.MAX_CONCURRENT_DOWNLOADS}</b>\n"
        f"📋 Queue Waiting: <b>{queue_stats['total_queued']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💿 Temp Storage: <b>{storage['temp_dir_size']}</b>\n"
        f"💿 Disk: <b>{storage['disk_used']}/{storage['disk_total']}</b> ({storage['disk_percent']}%)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱ Uptime: <b>{uptime}</b>\n"
        f"🔄 yt-dlp: <b>{Helpers.get_ytdlp_version()}</b>\n"
        f"🐍 Python: <b>{Helpers.get_python_version()}</b>\n"
        f"🔧 Maintenance: <b>{'ON' if Config.MAINTENANCE_MODE else 'OFF'}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )

    buttons = [
        [
            InlineKeyboardButton("📈 Full Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📋 Recent Logs", callback_data="admin_logs"),
        ],
        [
            InlineKeyboardButton("🔄 Restart", callback_data="admin_restart"),
            InlineKeyboardButton("⬆️ Update yt-dlp", callback_data="admin_update"),
        ],
        [
            InlineKeyboardButton("🧹 Cleanup Temp", callback_data="admin_cleanup"),
            InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance"),
        ],
    ]

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    stats = await db.get_stats()
    storage = file_manager.get_storage_stats()

    text = (
        f"📈 <b>Detailed Statistics</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Users</b>\n"
        f"  Total: {stats['total_users']}\n\n"
        f"📥 <b>Downloads</b>\n"
        f"  Today: {stats['downloads_today']}\n"
        f"  Total: {stats['total_downloads']}\n"
        f"  Data: {stats['total_data_mb']} MB\n\n"
        f"💾 <b>Storage</b>\n"
        f"  Temp: {storage['temp_dir_size']}\n"
        f"  Disk: {storage['disk_used']}/{storage['disk_total']}\n"
        f"  Usage: {storage['disk_percent']}%\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - send message to all users."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    message_text = " ".join(context.args) if context.args else ""
    if not message_text:
        await update.message.reply_text(
            "📢 <b>Usage:</b> /broadcast <message>\n\n"
            "Example: /broadcast Bot will be down for maintenance at 2AM.",
            parse_mode=ParseMode.HTML,
        )
        return

    user_ids = await db.get_all_user_ids()
    total = len(user_ids)
    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(
        f"📢 <b>Broadcasting to {total} users...</b>\n⏳ 0/{total}",
        parse_mode=ParseMode.HTML,
    )

    for i, uid in enumerate(user_ids):
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 <b>Announcement</b>\n\n{message_text}\n\n— @YTGrabDownBot",
                parse_mode=ParseMode.HTML,
            )
            sent += 1
        except Exception:
            failed += 1

        # Update progress every 50 messages
        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 <b>Broadcasting...</b>\n\n"
                    f"✅ Sent: {sent}\n❌ Failed: {failed}\n"
                    f"📊 Progress: {i+1}/{total}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

        await asyncio.sleep(0.05)  # Rate limit protection

    await status_msg.edit_text(
        f"📢 <b>Broadcast Complete!</b>\n\n"
        f"✅ Sent: <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total: <b>{total}</b>",
        parse_mode=ParseMode.HTML,
    )

    logger.info(f"📢 Broadcast: {sent}/{total} sent, {failed} failed")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    target = _get_target_user(update, context)
    if not target:
        await update.message.reply_text(
            "🚫 <b>Usage:</b> /ban <user_id or @username>\n\n"
            "Or reply to a user's message with /ban",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.create_user(target)  # Ensure user exists
    await db.ban_user(target, ban=True)
    await update.message.reply_text(
        f"🚫 <b>User {target} has been banned.</b>",
        parse_mode=ParseMode.HTML,
    )
    logger.info(f"🚫 Admin banned user {target}")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    target = _get_target_user(update, context)
    if not target:
        await update.message.reply_text(
            "✅ <b>Usage:</b> /unban <user_id>",
            parse_mode=ParseMode.HTML,
        )
        return

    await db.ban_user(target, ban=False)
    await update.message.reply_text(
        f"✅ <b>User {target} has been unbanned.</b>",
        parse_mode=ParseMode.HTML,
    )
    logger.info(f"✅ Admin unbanned user {target}")


async def setlimit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlimit command - set daily download limit."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    if not context.args:
        await update.message.reply_text(
            f"📊 Current limit: <b>{Config.RATE_LIMIT_PER_DAY}</b> downloads/day\n\n"
            f"<b>Usage:</b> /setlimit <number>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        new_limit = int(context.args[0])
        if new_limit < 1 or new_limit > 10000:
            raise ValueError
        Config.RATE_LIMIT_PER_DAY = new_limit
        await update.message.reply_text(
            f"✅ Daily limit set to <b>{new_limit}</b> downloads/day.",
            parse_mode=ParseMode.HTML,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Use 1-10000.")


async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /maintenance command - toggle maintenance mode."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    if context.args and context.args[0].lower() in ("on", "off", "true", "false"):
        Config.MAINTENANCE_MODE = context.args[0].lower() in ("on", "true")
    else:
        Config.MAINTENANCE_MODE = not Config.MAINTENANCE_MODE

    status = "🔧 ON" if Config.MAINTENANCE_MODE else "✅ OFF"
    await update.message.reply_text(
        f"Maintenance mode: <b>{status}</b>\n\n"
        f"{'⚠️ Users will see maintenance message.' if Config.MAINTENANCE_MODE else '✅ Bot is fully operational.'}",
        parse_mode=ParseMode.HTML,
    )
    logger.info(f"🔧 Maintenance mode: {Config.MAINTENANCE_MODE}")


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command - view recent logs."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    try:
        log_file = Config.LOG_FILE
        if log_file.exists():
            with open(log_file, "r") as f:
                lines = f.readlines()
                recent = lines[-30:]  # Last 30 lines
                log_text = "".join(recent)
                log_text = Helpers.truncate(log_text, 3900)

            await update.message.reply_text(
                f"📋 <b>Recent Logs (last 30 lines)</b>\n\n<code>{Helpers.escape_html(log_text)}</code>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text("📋 No log file found.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading logs: {e}")


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /update command - update yt-dlp."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    msg = await update.message.reply_text("⬆️ <b>Updating yt-dlp...</b>", parse_mode=ParseMode.HTML)

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-U", "yt-dlp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        new_version = Helpers.get_ytdlp_version()
        await msg.edit_text(
            f"✅ <b>yt-dlp updated!</b>\n\n"
            f"🔄 Version: <b>{new_version}</b>",
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"⬆️ yt-dlp updated to {new_version}")

    except Exception as e:
        await msg.edit_text(f"❌ Update failed: {e}", parse_mode=ParseMode.HTML)


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /restart command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Admin only command.")
        return

    await update.message.reply_text("🔄 <b>Restarting bot...</b>", parse_mode=ParseMode.HTML)
    logger.info("🔄 Admin requested restart")

    # The systemd service will auto-restart the bot
    import os
    os._exit(1)


async def admin_callback_handler(query, data: str):
    """Handle admin callback buttons."""
    if not is_admin(query.from_user.id):
        await query.answer("🚫 Admin only!", show_alert=True)
        return

    await query.answer()

    if data == "admin_stats":
        stats = await db.get_stats()
        storage = file_manager.get_storage_stats()
        text = (
            f"📈 <b>Full Stats</b>\n\n"
            f"Users: {stats['total_users']}\n"
            f"Downloads Today: {stats['downloads_today']}\n"
            f"Downloads Total: {stats['total_downloads']}\n"
            f"Data: {stats['total_data_mb']} MB\n"
            f"Temp: {storage['temp_dir_size']}\n"
            f"Disk: {storage['disk_percent']}%"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)

    elif data == "admin_logs":
        try:
            if Config.LOG_FILE.exists():
                with open(Config.LOG_FILE, "r") as f:
                    lines = f.readlines()[-20:]
                    log_text = Helpers.truncate("".join(lines), 3900)
                await query.edit_message_text(
                    f"📋 <b>Logs</b>\n\n<code>{Helpers.escape_html(log_text)}</code>",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await query.edit_message_text("No logs found.")
        except Exception as e:
            await query.edit_message_text(f"Error: {e}")

    elif data == "admin_cleanup":
        cleaned = Helpers.cleanup_old_files(0)  # Clean all
        file_manager.cleanup_user_files(0)
        await query.edit_message_text(
            f"🧹 <b>Cleanup Complete!</b>\n\nRemoved {cleaned} temp files.",
            parse_mode=ParseMode.HTML,
        )

    elif data == "admin_maintenance":
        Config.MAINTENANCE_MODE = not Config.MAINTENANCE_MODE
        status = "ON 🔧" if Config.MAINTENANCE_MODE else "OFF ✅"
        await query.edit_message_text(
            f"🔧 Maintenance: <b>{status}</b>",
            parse_mode=ParseMode.HTML,
        )

    elif data == "admin_update":
        await query.edit_message_text("⬆️ Updating yt-dlp...", parse_mode=ParseMode.HTML)
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", "-U", "yt-dlp",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            await query.edit_message_text(
                f"✅ Updated! yt-dlp: {Helpers.get_ytdlp_version()}",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Update failed: {e}")

    elif data == "admin_restart":
        await query.edit_message_text("🔄 Restarting...", parse_mode=ParseMode.HTML)
        import os
        os._exit(1)


def _get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Extract target user ID from command or reply."""
    # From reply
    if update.message and update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id

    # From args
    if context.args:
        arg = context.args[0]
        # Try as user ID
        try:
            return int(arg.replace("@", ""))
        except ValueError:
            pass

    return None
