"""
YTGrab Bot - Configuration Module
Bot: @YTGrabDownBot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration loaded from environment variables."""

    # ─── Bot Info ───────────────────────────────────────────
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "YTGrabDownBot")
    BOT_NAME: str = os.getenv("BOT_NAME", "YTGrab Bot")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

    # ─── Paths ──────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).parent
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/ytgrab"))
    DOWNLOADS_DIR: Path = TEMP_DIR / "downloads"
    PROCESSING_DIR: Path = TEMP_DIR / "processing"
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    DB_PATH: Path = Path(os.getenv("DB_PATH", "./data/ytgrab.db"))
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "./logs/bot.log"))

    # ─── Download Settings ──────────────────────────────────
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "2000"))
    MAX_DOWNLOAD_DURATION_MIN: int = int(os.getenv("MAX_DOWNLOAD_DURATION_MIN", "180"))
    MAX_PLAYLIST_ITEMS: int = int(os.getenv("MAX_PLAYLIST_ITEMS", "100"))
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "10"))
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))
    CLEANUP_INTERVAL_MIN: int = int(os.getenv("CLEANUP_INTERVAL_MIN", "30"))

    # ─── Rate Limiting ──────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "50"))
    RATE_LIMIT_PER_DAY: int = int(os.getenv("RATE_LIMIT_PER_DAY", "100"))

    # ─── Local API (for large files) ───────────────────────
    USE_LOCAL_API: bool = os.getenv("USE_LOCAL_API", "false").lower() == "true"
    LOCAL_API_URL: str = os.getenv("LOCAL_API_URL", "http://localhost:8081")

    # ─── Logging ────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ─── Telegram API Limits ────────────────────────────────
    TELEGRAM_MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    TELEGRAM_MAX_FILE_SIZE_LOCAL: int = 2000 * 1024 * 1024  # 2GB
    TELEGRAM_MAX_MESSAGE_LENGTH: int = 4096

    # ─── Supported Formats ──────────────────────────────────
    AUDIO_FORMATS: list = ["mp3", "m4a", "flac", "ogg", "wav", "opus", "aac"]
    VIDEO_FORMATS: list = ["mp4", "webm", "mkv", "avi"]
    AUDIO_BITRATES: list = [64, 128, 192, 256, 320]
    VIDEO_RESOLUTIONS: list = [144, 240, 360, 480, 720, 1080, 1440, 2160]

    # ─── yt-dlp Settings ────────────────────────────────────
    YTDLP_OPTIONS: dict = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        "extractor_retries": 3,
    }

    @classmethod
    def initialize_dirs(cls):
        """Create necessary directories."""
        dirs = [
            cls.TEMP_DIR,
            cls.DOWNLOADS_DIR,
            cls.PROCESSING_DIR,
            cls.DATA_DIR,
            cls.LOGS_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN is not set! Get one from @BotFather")
        if not cls.ADMIN_ID:
            raise ValueError("❌ ADMIN_ID is not set! Get yours from @userinfobot")
        return True


# Initialize directories on import
Config.initialize_dirs()
