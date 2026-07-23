"""
YTGrab Bot - File Manager
Handles file operations, cleanup, splitting, and size management.
"""

import os
import shutil
import asyncio
import zipfile
from pathlib import Path
from typing import Optional
from loguru import logger

from config import Config
from utils.helpers import Helpers


class FileManager:
    """Manages file operations for downloads."""

    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
        self.downloads_dir = Config.DOWNLOADS_DIR

    # ─── User File Operations ───────────────────────────────

    def get_user_dir(self, user_id: int) -> Path:
        """Get or create user's temp directory."""
        user_dir = self.downloads_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def cleanup_user_files(self, user_id: int):
        """Delete all temp files for a user."""
        user_dir = self.downloads_dir / str(user_id)
        if user_dir.exists():
            for f in user_dir.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                    elif f.is_dir():
                        shutil.rmtree(f)
                except Exception as e:
                    logger.warning(f"Cleanup error for {f}: {e}")
            try:
                user_dir.rmdir()
            except Exception:
                pass

    def find_file(self, user_id: int, extension: str = None) -> Optional[Path]:
        """Find the most recent downloaded file for a user."""
        user_dir = self.downloads_dir / str(user_id)
        if not user_dir.exists():
            return None

        if extension:
            files = list(user_dir.glob(f"*.{extension}"))
        else:
            files = [f for f in user_dir.iterdir() if f.is_file()]

        if files:
            return max(files, key=lambda f: f.stat().st_mtime)
        return None

    def find_all_files(self, user_id: int, extension: str = None) -> list:
        """Find all files for a user."""
        user_dir = self.downloads_dir / str(user_id)
        if not user_dir.exists():
            return []

        if extension:
            return sorted(user_dir.glob(f"*.{extension}"), key=lambda f: f.stat().st_mtime)
        return sorted(
            [f for f in user_dir.iterdir() if f.is_file()],
            key=lambda f: f.stat().st_mtime
        )

    # ─── File Size Operations ───────────────────────────────

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except Exception:
            return 0

    def is_within_limit(self, file_path: Path) -> bool:
        """Check if file is within Telegram's upload limit."""
        size = self.get_file_size(file_path)
        max_size = (
            Config.TELEGRAM_MAX_FILE_SIZE_LOCAL
            if Config.USE_LOCAL_API
            else Config.TELEGRAM_MAX_FILE_SIZE
        )
        return size <= max_size

    def needs_splitting(self, file_path: Path) -> bool:
        """Check if file needs to be split."""
        size = self.get_file_size(file_path)
        max_size = (
            Config.TELEGRAM_MAX_FILE_SIZE_LOCAL
            if Config.USE_LOCAL_API
            else Config.TELEGRAM_MAX_FILE_SIZE
        )
        return size > max_size

    async def split_file(self, file_path: Path, max_size_mb: int = 49) -> list:
        """Split a large file into parts."""
        max_size = max_size_mb * 1024 * 1024
        file_size = self.get_file_size(file_path)
        parts = []
        part_num = 1

        output_dir = file_path.parent
        stem = file_path.stem
        suffix = file_path.suffix

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(max_size)
                if not chunk:
                    break

                part_path = output_dir / f"{stem}_Part{part_num}{suffix}"
                with open(part_path, 'wb') as pf:
                    pf.write(chunk)
                parts.append(part_path)
                part_num += 1

        logger.info(f"📦 Split {file_path.name} into {len(parts)} parts")
        return parts

    # ─── ZIP Operations ─────────────────────────────────────

    async def create_zip(self, files: list, output_name: str, user_id: int) -> Optional[Path]:
        """Create a ZIP archive from multiple files."""
        user_dir = self.get_user_dir(user_id)
        zip_path = user_dir / f"{Helpers.sanitize_filename(output_name)}.zip"

        def _create():
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    if f.exists():
                        zf.write(f, f.name)

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _create)
            logger.info(f"📦 Created ZIP: {zip_path.name} ({len(files)} files)")
            return zip_path
        except Exception as e:
            logger.error(f"ZIP creation error: {e}")
            return None

    # ─── GIF Conversion ─────────────────────────────────────

    async def convert_to_gif(
        self, video_path: Path, start_time: str = "0",
        duration: int = 10, width: int = 480, fps: int = 15
    ) -> Optional[Path]:
        """Convert video segment to GIF using FFmpeg."""
        output_path = video_path.parent / f"{video_path.stem}.gif"

        cmd = (
            f'ffmpeg -y -ss {start_time} -t {duration} '
            f'-i "{video_path}" '
            f'-vf "fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];'
            f'[s0]palettegen[p];[s1][p]paletteuse" '
            f'-loop 0 "{output_path}"'
        )

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            if output_path.exists():
                logger.info(f"🎞️ GIF created: {output_path.name}")
                return output_path
            return None

        except Exception as e:
            logger.error(f"GIF conversion error: {e}")
            return None

    # ─── Audio Splitting (Chapters) ─────────────────────────

    async def split_audio_chapters(
        self, audio_path: Path, chapters: list
    ) -> list:
        """Split audio into chapters using FFmpeg."""
        parts = []
        output_dir = audio_path.parent

        for i, chapter in enumerate(chapters):
            start = chapter.get("start_time", 0)
            end = chapter.get("end_time", 0)
            title = chapter.get("title", f"Chapter {i+1}")
            safe_title = Helpers.sanitize_filename(title)

            output_path = output_dir / f"{i+1:02d} - {safe_title}{audio_path.suffix}"

            cmd = (
                f'ffmpeg -y -i "{audio_path}" '
                f'-ss {start} -to {end} '
                f'-c copy "{output_path}"'
            )

            try:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await process.communicate()
                if output_path.exists():
                    parts.append(output_path)
            except Exception as e:
                logger.error(f"Chapter split error: {e}")

        return parts

    # ─── Cleanup Operations ─────────────────────────────────

    async def scheduled_cleanup(self):
        """Periodic cleanup of old temp files."""
        cleaned = Helpers.cleanup_old_files(Config.CLEANUP_INTERVAL_MIN)

        # Check disk space
        if not Helpers.check_disk_space():
            logger.warning("🚨 Low disk space! Running emergency cleanup...")
            Helpers.emergency_cleanup()

        return cleaned

    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        temp_size = Helpers.get_temp_dir_size()
        disk = Helpers.get_disk_usage()
        return {
            "temp_dir_size": Helpers.format_filesize(temp_size),
            "temp_dir_bytes": temp_size,
            "disk_total": disk["total"],
            "disk_used": disk["used"],
            "disk_free": disk["free"],
            "disk_percent": disk["percent"],
        }


# Singleton
file_manager = FileManager()
