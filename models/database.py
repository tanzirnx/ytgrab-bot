"""
YTGrab Bot - Database Module
SQLite database for user preferences and download tracking.
"""

import aiosqlite
from pathlib import Path
from datetime import datetime, date
from typing import Optional
from loguru import logger

from config import Config


class Database:
    """Async SQLite database manager."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Create tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'en',
                    default_format TEXT DEFAULT 'mp3',
                    default_quality TEXT DEFAULT 'best',
                    default_audio_bitrate INTEGER DEFAULT 320,
                    default_video_resolution TEXT DEFAULT '1080',
                    auto_thumbnail BOOLEAN DEFAULT 1,
                    auto_subtitles BOOLEAN DEFAULT 0,
                    subtitle_language TEXT DEFAULT 'en',
                    filename_template TEXT DEFAULT '{title}.{ext}',
                    notifications BOOLEAN DEFAULT 1,
                    is_banned BOOLEAN DEFAULT 0,
                    is_admin BOOLEAN DEFAULT 0,
                    is_whitelisted BOOLEAN DEFAULT 0,
                    downloads_today INTEGER DEFAULT 0,
                    total_downloads INTEGER DEFAULT 0,
                    last_reset_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT,
                    title TEXT,
                    format TEXT,
                    file_size INTEGER,
                    duration_seconds INTEGER,
                    status TEXT DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS rate_limits (
                    user_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, timestamp)
                );

                CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username);
                CREATE INDEX IF NOT EXISTS idx_history_user 
                    ON download_history(user_id);
                CREATE INDEX IF NOT EXISTS idx_rate_user 
                    ON rate_limits(user_id);
            """)
            await db.commit()
        logger.info("✅ Database initialized successfully")

    # ─── User Management ────────────────────────────────────

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Create a new user or update existing."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_active)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_active = excluded.last_active
            """, (user_id, username, first_name, datetime.now().isoformat()))
            await db.commit()

    async def update_user_preference(self, user_id: int, key: str, value):
        """Update a user preference."""
        allowed_keys = [
            'language', 'default_format', 'default_quality',
            'default_audio_bitrate', 'default_video_resolution',
            'auto_thumbnail', 'auto_subtitles', 'subtitle_language',
            'filename_template', 'notifications'
        ]
        if key not in allowed_keys:
            raise ValueError(f"Invalid preference key: {key}")

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {key} = ? WHERE user_id = ?",
                (value, user_id)
            )
            await db.commit()

    async def is_banned(self, user_id: int) -> bool:
        """Check if user is banned."""
        user = await self.get_user(user_id)
        if user:
            return bool(user.get('is_banned', 0))
        return False

    async def ban_user(self, user_id: int, ban: bool = True):
        """Ban or unban a user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_banned = ? WHERE user_id = ?",
                (int(ban), user_id)
            )
            await db.commit()

    async def increment_downloads(self, user_id: int):
        """Increment user's download count."""
        today = date.today().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            # Reset daily count if new day
            await db.execute("""
                UPDATE users SET downloads_today = 0, last_reset_date = ?
                WHERE user_id = ? AND last_reset_date != ?
            """, (today, user_id, today))

            # Increment counts
            await db.execute("""
                UPDATE users SET 
                    downloads_today = downloads_today + 1,
                    total_downloads = total_downloads + 1
                WHERE user_id = ?
            """, (user_id,))
            await db.commit()

    async def get_downloads_today(self, user_id: int) -> int:
        """Get user's download count for today."""
        today = date.today().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT downloads_today, last_reset_date FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[1] == today:
                    return row[0]
                return 0

    # ─── Download History ───────────────────────────────────

    async def add_download_history(
        self, user_id: int, url: str, title: str,
        format: str, file_size: int, duration: int = 0
    ):
        """Record a download in history."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO download_history 
                (user_id, url, title, format, file_size, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, url, title, format, file_size, duration))
            await db.commit()

    # ─── Statistics ─────────────────────────────────────────

    async def get_stats(self) -> dict:
        """Get bot statistics."""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}

            async with db.execute("SELECT COUNT(*) FROM users") as c:
                stats['total_users'] = (await c.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM download_history") as c:
                stats['total_downloads'] = (await c.fetchone())[0]

            today = date.today().isoformat()
            async with db.execute(
                "SELECT COUNT(*) FROM download_history WHERE DATE(created_at) = ?",
                (today,)
            ) as c:
                stats['downloads_today'] = (await c.fetchone())[0]

            async with db.execute(
                "SELECT SUM(file_size) FROM download_history"
            ) as c:
                stats['total_data_mb'] = round(
                    ((await c.fetchone())[0] or 0) / (1024 * 1024), 2
                )

            return stats

    async def get_all_user_ids(self) -> list:
        """Get all user IDs (for broadcast)."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id FROM users WHERE is_banned = 0"
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]


# Singleton instance
db = Database()
