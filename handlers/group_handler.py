"""
YTGrab Bot - Group Chat Handler (Phase 3)
Commands: /gsettings, /gallow, /gdeny, /glimit
Handles bot behavior in group chats.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatMemberStatus
from loguru import logger

from config import Config
from models.database import db


async def gsettings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gsettings - group settings menu."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("⚠️ This command works only in groups.")
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    # Check if user is group admin
    if not await _is_group_admin(context, chat_id, user.id):
        await update.message.reply_text("🚫 Only group admins can change bot settings.")
        return

    group = await _get_group_settings(chat_id)

    status = "✅ Enabled" if group.get("enabled", 1) else "❌ Disabled"
    limit = group.get("max_downloads_per_user", 5)
    max_size = group.get("max_file_size_mb", 100)
    silent = "✅ ON" if group.get("silent_mode", 0) else "❌ OFF"

    text = (
        f"⚙️ <b>Group Settings</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot Status: <b>{status}</b>\n"
        f"📥 Per-User Limit: <b>{limit}/day</b>\n"
        f"📦 Max File Size: <b>{max_size} MB</b>\n"
        f"🤫 Silent Mode: <b>{silent}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💡 Use buttons below to change:"
    )

    buttons = [
        [
            InlineKeyboardButton(
                f"{'🟢 Disable' if group.get('enabled', 1) else '🔴 Enable'}",
                callback_data=f"g_toggle|{chat_id}"
            ),
            InlineKeyboardButton(
                f"{'🔊 Silent ON' if group.get('silent_mode', 0) else '🔇 Silent OFF'}",
                callback_data=f"g_silent|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton("📥 Limit: 5", callback_data=f"g_limit_5|{chat_id}"),
            InlineKeyboardButton("📥 Limit: 10", callback_data=f"g_limit_10|{chat_id}"),
            InlineKeyboardButton("📥 Limit: 20", callback_data=f"g_limit_20|{chat_id}"),
        ],
        [
            InlineKeyboardButton("📦 50MB", callback_data=f"g_size_50|{chat_id}"),
            InlineKeyboardButton("📦 100MB", callback_data=f"g_size_100|{chat_id}"),
            InlineKeyboardButton("📦 200MB", callback_data=f"g_size_200|{chat_id}"),
        ],
    ]

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def gallow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gallow - enable bot in group."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("⚠️ This command works only in groups.")
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if not await _is_group_admin(context, chat_id, user.id):
        await update.message.reply_text("🚫 Only group admins can use this command.")
        return

    await _update_group_setting(chat_id, "enabled", 1)
    await update.message.reply_text(
        "✅ <b>Bot enabled in this group!</b>\n\n"
        "Members can now paste URLs to download media.",
        parse_mode=ParseMode.HTML,
    )
    logger.info(f"✅ Bot enabled in group {chat_id}")


async def gdeny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gdeny - disable bot in group."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("⚠️ This command works only in groups.")
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if not await _is_group_admin(context, chat_id, user.id):
        await update.message.reply_text("🚫 Only group admins can use this command.")
        return

    await _update_group_setting(chat_id, "enabled", 0)
    await update.message.reply_text(
        "❌ <b>Bot disabled in this group.</b>\n\n"
        "Use /gallow to re-enable.",
        parse_mode=ParseMode.HTML,
    )
    logger.info(f"❌ Bot disabled in group {chat_id}")


async def glimit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /glimit - set per-user download limit in group."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("⚠️ This command works only in groups.")
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if not await _is_group_admin(context, chat_id, user.id):
        await update.message.reply_text("🚫 Only group admins can use this command.")
        return

    if not context.args:
        group = await _get_group_settings(chat_id)
        current = group.get("max_downloads_per_user", 5)
        await update.message.reply_text(
            f"📥 Current group limit: <b>{current} downloads/user/day</b>\n\n"
            f"<b>Usage:</b> /glimit <number>\n"
            f"Example: /glimit 10",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        limit = int(context.args[0])
        if limit < 1 or limit > 100:
            raise ValueError
        await _update_group_setting(chat_id, "max_downloads_per_user", limit)
        await update.message.reply_text(
            f"✅ Group limit set to <b>{limit} downloads/user/day</b>",
            parse_mode=ParseMode.HTML,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Use 1-100.")


async def group_url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URLs in group chats (checks group settings)."""
    if update.effective_chat.type == "private":
        return  # Let private handler deal with it

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if bot is enabled in group
    group = await _get_group_settings(chat_id)
    if not group.get("enabled", 1):
        return  # Bot disabled, ignore

    # Check silent mode (only respond when mentioned)
    if group.get("silent_mode", 0):
        bot_username = Config.BOT_USERNAME.lower()
        text = update.message.text.lower() if update.message.text else ""
        if f"@{bot_username}" not in text and not update.message.reply_to_message:
            return

    # Check per-user group limit
    # (simplified - in production, track per-group per-user)

    # Forward to main URL handler
    from handlers.download_handler import url_handler
    await url_handler(update, context)


async def group_callback_handler(query, data: str):
    """Handle group settings callback buttons."""
    parts = data.split("|")
    action = parts[0]
    chat_id = int(parts[1]) if len(parts) > 1 else 0

    # Verify admin
    user_id = query.from_user.id
    if not await _is_group_admin_from_query(query, chat_id, user_id):
        await query.answer("🚫 Admin only!", show_alert=True)
        return

    await query.answer()

    if action == "g_toggle":
        group = await _get_group_settings(chat_id)
        new_val = 0 if group.get("enabled", 1) else 1
        await _update_group_setting(chat_id, "enabled", new_val)
        status = "✅ Enabled" if new_val else "❌ Disabled"
        await query.edit_message_text(
            f"🤖 Bot status: <b>{status}</b>",
            parse_mode=ParseMode.HTML,
        )

    elif action == "g_silent":
        group = await _get_group_settings(chat_id)
        new_val = 0 if group.get("silent_mode", 0) else 1
        await _update_group_setting(chat_id, "silent_mode", new_val)
        status = "🤫 ON" if new_val else "🔊 OFF"
        await query.edit_message_text(
            f"Silent mode: <b>{status}</b>",
            parse_mode=ParseMode.HTML,
        )

    elif action.startswith("g_limit_"):
        limit = int(action.replace("g_limit_", ""))
        await _update_group_setting(chat_id, "max_downloads_per_user", limit)
        await query.edit_message_text(
            f"📥 Group limit: <b>{limit}/user/day</b>",
            parse_mode=ParseMode.HTML,
        )

    elif action.startswith("g_size_"):
        size = int(action.replace("g_size_", ""))
        await _update_group_setting(chat_id, "max_file_size_mb", size)
        await query.edit_message_text(
            f"📦 Max file size: <b>{size} MB</b>",
            parse_mode=ParseMode.HTML,
        )


# ─── Internal Helpers ───────────────────────────────────────

async def _is_group_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    """Check if user is admin in the group."""
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def _is_group_admin_from_query(query, chat_id: int, user_id: int) -> bool:
    """Check admin from callback query."""
    try:
        member = await query.bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def _get_group_settings(chat_id: int) -> dict:
    """Get group settings from database."""
    import aiosqlite
    from config import Config as Cfg

    try:
        async with aiosqlite.connect(Cfg.DB_PATH) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute(
                "SELECT * FROM group_settings WHERE group_id = ?", (chat_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
    except Exception:
        pass

    return {
        "group_id": chat_id,
        "enabled": 1,
        "max_downloads_per_user": 5,
        "max_file_size_mb": 100,
        "silent_mode": 0,
    }


async def _update_group_setting(chat_id: int, key: str, value):
    """Update a group setting."""
    import aiosqlite
    from config import Config as Cfg

    async with aiosqlite.connect(Cfg.DB_PATH) as db_conn:
        # Ensure group exists
        await db_conn.execute("""
            INSERT INTO group_settings (group_id, enabled, max_downloads_per_user, max_file_size_mb, silent_mode)
            VALUES (?, 1, 5, 100, 0)
            ON CONFLICT(group_id) DO NOTHING
        """, (chat_id,))

        await db_conn.execute(
            f"UPDATE group_settings SET {key} = ? WHERE group_id = ?",
            (value, chat_id)
        )
        await db_conn.commit()
