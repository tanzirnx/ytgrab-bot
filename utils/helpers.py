"""
YTGrab Bot - Helper Utilities
"""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from config import Config


class Helpers:
    """General utility functions."""

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format seconds to HH:MM:SS or MM:SS."""
        if not seconds or seconds <= 0:
            return "0:00"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @staticmethod
    def format_filesize(bytes: int) -> str:
        """Format bytes to human-readable size."""
        if bytes <= 0:
            return "Unknown"
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_idx = 0
        size = float(bytes)
        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1
        return f"{size:.1f} {units[unit_idx]}"

    @staticmethod
    def format_number(num: int) -> str:
        """Format large numbers (1.2M, 3.4K)."""
        if num is None:
            return "0"
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

    @staticmethod
    def format_uptime(start_time: float) -> str:
        """Format uptime from start timestamp."""
        delta = timedelta(seconds=time.time() - start_time)
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @staticmethod
    def progress_bar(percent: float, length: int = 20) -> str:
        """Generate text progress bar."""
        percent = max(0, min(100, percent))
        filled = int(length * percent / 100)
        bar = "━" * filled + "░" * (length - filled)
        return f"[{bar}]"

    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    @staticmethod
    def truncate(text: str, max_length: int = 4000) -> str:
        """Truncate text to max length with ellipsis."""
        if not text or len(text) <= max_length:
            return text or ""
        return text[:max_length - 3] + "..."

    @staticmethod
    def get_disk_usage() -> dict:
        """Get disk usage for temp directory."""
        try:
            total, used, free = shutil.disk_usage(str(Config.TEMP_DIR))
            return {
                "total": Helpers.format_filesize(total),
                "used": Helpers.format_filesize(used),
                "free": Helpers.format_filesize(free),
                "percent": round(used / total * 100, 1),
            }
        except Exception:
            return {"total": "?", "used": "?", "free": "?", "percent": 0}

    @staticmethod
    def get_temp_dir_size() -> int:
        """Get total size of temp directory in bytes."""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(Config.TEMP_DIR):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except Exception:
            pass
        return total

    @staticmethod
    def cleanup_old_files(max_age_minutes: int = 30):
        """Delete files older than max_age_minutes."""
        cutoff = time.time() - (max_age_minutes * 60)
        cleaned = 0
        try:
            for dirpath, dirnames, filenames in os.walk(Config.TEMP_DIR):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp) and os.path.getmtime(fp) < cutoff:
                        os.remove(fp)
                        cleaned += 1
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
        if cleaned > 0:
            logger.info(f"🧹 Cleaned {cleaned} old files")
        return cleaned

    @staticmethod
    def emergency_cleanup():
        """Delete ALL temp files (when disk > 90%)."""
        try:
            shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)
            Config.initialize_dirs()
            logger.warning("🚨 Emergency cleanup executed!")
        except Exception as e:
            logger.error(f"Emergency cleanup failed: {e}")

    @staticmethod
    def check_disk_space() -> bool:
        """Check if there's enough disk space. Returns False if < 10% free."""
        try:
            _, _, free = shutil.disk_usage(str(Config.TEMP_DIR))
            total, _, _ = shutil.disk_usage(str(Config.TEMP_DIR))
            if free / total < 0.10:
                logger.warning(f"⚠️ Low disk space: {Helpers.format_filesize(free)} free")
                return False
            return True
        except Exception:
            return True

    @staticmethod
    def get_ytdlp_version() -> str:
        """Get yt-dlp version string."""
        try:
            import yt_dlp
            return yt_dlp.version.__version__
        except Exception:
            return "unknown"

    @staticmethod
    def get_python_version() -> str:
        """Get Python version string."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
