"""
YTGrab Bot - Downloader Service
yt-dlp wrapper with progress tracking and format handling.
"""

import os
import asyncio
import time
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field

import yt_dlp
from loguru import logger

from config import Config


@dataclass
class DownloadProgress:
    """Track download progress."""
    percent: float = 0.0
    speed: str = "0 B/s"
    eta: str = "calculating..."
    downloaded_bytes: int = 0
    total_bytes: int = 0
    status: str = "downloading"  # downloading, processing, uploading, done, error


@dataclass
class MediaInfo:
    """Media information extracted from URL."""
    title: str = ""
    duration: int = 0  # seconds
    duration_str: str = ""
    uploader: str = ""
    views: int = 0
    likes: int = 0
    description: str = ""
    thumbnail_url: str = ""
    webpage_url: str = ""
    extractor: str = ""
    formats: list = field(default_factory=list)
    subtitles: list = field(default_factory=list)
    is_live: bool = False
    is_playlist: bool = False
    playlist_count: int = 0
    file_size: int = 0
    error: str = ""


class Downloader:
    """yt-dlp download engine wrapper."""

    def __init__(self):
        self.temp_dir = Config.DOWNLOADS_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    # ─── Info Extraction ────────────────────────────────────

    async def extract_info(self, url: str) -> MediaInfo:
        """Extract media information without downloading."""
        info = MediaInfo(webpage_url=url)

        def _extract():
            opts = {
                **Config.YTDLP_OPTIONS,
                "skip_download": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, _extract)

            if not data:
                info.error = "No data extracted"
                return info

            # Handle playlist
            if data.get("_type") == "playlist":
                info.is_playlist = True
                info.title = data.get("title", "Unknown Playlist")
                info.playlist_count = data.get("playlist_count", len(data.get("entries", [])))
                return info

            # Single video/audio
            info.title = data.get("title", "Unknown")
            info.duration = data.get("duration", 0) or 0
            info.duration_str = self._format_duration(info.duration)
            info.uploader = data.get("uploader", data.get("channel", "Unknown"))
            info.views = data.get("view_count", 0) or 0
            info.likes = data.get("like_count", 0) or 0
            info.description = data.get("description", "")[:500]
            info.thumbnail_url = data.get("thumbnail", "")
            info.extractor = data.get("extractor", "unknown")
            info.is_live = data.get("is_live", False)

            # Available formats
            formats = data.get("formats", [])
            info.formats = self._parse_formats(formats)

            # Available subtitles
            subs = data.get("subtitles", {})
            auto_subs = data.get("automatic_captions", {})
            info.subtitles = list(set(list(subs.keys()) + list(auto_subs.keys())))

            # Estimate file size
            info.file_size = data.get("filesize", 0) or data.get("filesize_approx", 0) or 0

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "Private video" in error_msg:
                info.error = "private"
            elif "age" in error_msg.lower():
                info.error = "age_restricted"
            elif "not found" in error_msg.lower() or "unavailable" in error_msg.lower():
                info.error = "not_found"
            elif "copyright" in error_msg.lower() or "blocked" in error_msg.lower():
                info.error = "copyright"
            else:
                info.error = f"download_error: {error_msg[:200]}"
            logger.error(f"Extract info error: {error_msg}")

        except Exception as e:
            info.error = f"unexpected: {str(e)[:200]}"
            logger.error(f"Unexpected error in extract_info: {e}")

        return info

    # ─── Audio Download ─────────────────────────────────────

    async def download_audio(
        self,
        url: str,
        user_id: int,
        format: str = "mp3",
        bitrate: int = 320,
        progress_callback: Optional[Callable] = None,
        embed_thumbnail: bool = True,
    ) -> Optional[Path]:
        """Download audio from URL."""
        output_path = self.temp_dir / str(user_id)
        output_path.mkdir(parents=True, exist_ok=True)
        output_template = str(output_path / "%(title).200s.%(ext)s")

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": str(bitrate),
            },
        ]

        if embed_thumbnail and format in ["mp3", "m4a", "flac", "ogg"]:
            postprocessors.append({"key": "EmbedThumbnail"})
            postprocessors.append({
                "key": "FFmpegMetadata",
                "add_metadata": True,
            })

        opts = {
            **Config.YTDLP_OPTIONS,
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": postprocessors,
            "progress_hooks": [self._make_progress_hook(progress_callback)],
            "noplaylist": True,
        }

        return await self._execute_download(opts, url, user_id, format)

    # ─── Video Download ─────────────────────────────────────

    async def download_video(
        self,
        url: str,
        user_id: int,
        resolution: str = "1080",
        format: str = "mp4",
        progress_callback: Optional[Callable] = None,
        embed_subtitles: bool = False,
        subtitle_lang: str = "en",
    ) -> Optional[Path]:
        """Download video from URL."""
        output_path = self.temp_dir / str(user_id)
        output_path.mkdir(parents=True, exist_ok=True)
        output_template = str(output_path / "%(title).200s.%(ext)s")

        # Format selection based on resolution
        if resolution == "best":
            format_str = f"bestvideo[ext={format}]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        elif resolution == "worst":
            format_str = "worstvideo+worstaudio/worst"
        else:
            format_str = (
                f"bestvideo[height<={resolution}][ext={format}]"
                f"+bestaudio[ext=m4a]/"
                f"bestvideo[height<={resolution}]+bestaudio/"
                f"best[height<={resolution}]"
            )

        postprocessors = [
            {"key": "FFmpegVideoConvertor", "preferedformat": format},
        ]

        if embed_subtitles:
            postprocessors.append({
                "key": "FFmpegEmbedSubtitle",
                "already_have_subtitle": False,
            })

        opts = {
            **Config.YTDLP_OPTIONS,
            "format": format_str,
            "outtmpl": output_template,
            "postprocessors": postprocessors,
            "progress_hooks": [self._make_progress_hook(progress_callback)],
            "merge_output_format": format,
            "noplaylist": True,
        }

        if embed_subtitles:
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = True
            opts["subtitleslangs"] = [subtitle_lang]

        return await self._execute_download(opts, url, user_id, format)

    # ─── Thumbnail Download ─────────────────────────────────

    async def download_thumbnail(
        self, url: str, user_id: int
    ) -> Optional[Path]:
        """Download video thumbnail."""
        output_path = self.temp_dir / str(user_id)
        output_path.mkdir(parents=True, exist_ok=True)
        output_template = str(output_path / "%(title).200s_thumb.%(ext)s")

        opts = {
            **Config.YTDLP_OPTIONS,
            "skip_download": True,
            "writethumbnail": True,
            "outtmpl": output_template,
            "noplaylist": True,
        }

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _download)

            # Find the thumbnail file
            for f in output_path.iterdir():
                if "_thumb" in f.name and f.suffix in [".jpg", ".png", ".webp"]:
                    return f
            return None

        except Exception as e:
            logger.error(f"Thumbnail download error: {e}")
            return None

    # ─── Subtitle Download ──────────────────────────────────

    async def download_subtitles(
        self, url: str, user_id: int, lang: str = "en", format: str = "srt"
    ) -> Optional[Path]:
        """Download subtitles for a video."""
        output_path = self.temp_dir / str(user_id)
        output_path.mkdir(parents=True, exist_ok=True)
        output_template = str(output_path / "%(title).200s.%(ext)s")

        opts = {
            **Config.YTDLP_OPTIONS,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [lang],
            "subtitlesformat": format,
            "outtmpl": output_template,
            "noplaylist": True,
        }

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _download)

            # Find subtitle file
            for f in output_path.iterdir():
                if f.suffix in [".srt", ".vtt", ".ass", ".json3"]:
                    return f
            return None

        except Exception as e:
            logger.error(f"Subtitle download error: {e}")
            return None

    # ─── Internal Methods ───────────────────────────────────

    async def _execute_download(
        self, opts: dict, url: str, user_id: int, format: str
    ) -> Optional[Path]:
        """Execute download in thread executor."""
        output_path = self.temp_dir / str(user_id)

        def _download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _download)

            # Find the downloaded file
            downloaded_file = self._find_downloaded_file(output_path, format)
            if downloaded_file:
                logger.info(f"✅ Download complete: {downloaded_file.name} ({downloaded_file.stat().st_size / 1024 / 1024:.2f} MB)")
                return downloaded_file

            logger.warning("Download completed but file not found")
            return None

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected download error: {e}")
            raise

    def _find_downloaded_file(self, directory: Path, format: str) -> Optional[Path]:
        """Find the most recently downloaded file."""
        files = list(directory.glob(f"*.{format}"))
        if not files:
            # Try any media file
            for ext in Config.AUDIO_FORMATS + Config.VIDEO_FORMATS:
                files = list(directory.glob(f"*.{ext}"))
                if files:
                    break
        if files:
            return max(files, key=lambda f: f.stat().st_mtime)
        return None

    def _make_progress_hook(self, callback: Optional[Callable]):
        """Create a progress hook for yt-dlp."""
        def hook(d):
            if callback and d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                speed = d.get("speed", 0) or 0
                eta = d.get("eta", 0) or 0

                percent = (downloaded / total * 100) if total > 0 else 0

                progress = DownloadProgress(
                    percent=round(percent, 1),
                    speed=self._format_speed(speed),
                    eta=self._format_eta(eta),
                    downloaded_bytes=downloaded,
                    total_bytes=total,
                    status="downloading",
                )
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            callback(progress), loop
                        )
                except Exception:
                    pass

        return hook

    # ─── Utility Methods ────────────────────────────────────

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds to HH:MM:SS."""
        if not seconds:
            return "0:00"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    @staticmethod
    def _format_speed(bytes_per_sec: float) -> str:
        """Format download speed."""
        if bytes_per_sec <= 0:
            return "0 B/s"
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        unit_idx = 0
        speed = bytes_per_sec
        while speed >= 1024 and unit_idx < len(units) - 1:
            speed /= 1024
            unit_idx += 1
        return f"{speed:.1f} {units[unit_idx]}"

    @staticmethod
    def _format_eta(seconds: int) -> str:
        """Format ETA."""
        if seconds <= 0:
            return "calculating..."
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"

    @staticmethod
    def _parse_formats(formats: list) -> list:
        """Parse available formats into readable list."""
        parsed = []
        seen = set()
        for f in formats:
            height = f.get("height")
            ext = f.get("ext", "")
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            filesize = f.get("filesize", 0) or 0

            if height and vcodec != "none":
                key = f"{height}p_{ext}"
                if key not in seen:
                    seen.add(key)
                    parsed.append({
                        "resolution": f"{height}p",
                        "ext": ext,
                        "has_audio": acodec != "none",
                        "filesize": filesize,
                        "format_id": f.get("format_id", ""),
                    })
        return sorted(parsed, key=lambda x: int(x["resolution"].replace("p", "")), reverse=True)

    # ─── Cleanup ────────────────────────────────────────────

    @staticmethod
    def cleanup_user_files(user_id: int):
        """Delete all temp files for a user."""
        user_dir = Config.DOWNLOADS_DIR / str(user_id)
        if user_dir.exists():
            for f in user_dir.iterdir():
                try:
                    f.unlink()
                except Exception as e:
                    logger.warning(f"Cleanup error: {e}")
            try:
                user_dir.rmdir()
            except Exception:
                pass

    @staticmethod
    def cleanup_all():
        """Emergency cleanup of all temp files."""
        import shutil
        if Config.TEMP_DIR.exists():
            shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)
            Config.TEMP_DIR.mkdir(parents=True, exist_ok=True)
            (Config.TEMP_DIR / "downloads").mkdir(exist_ok=True)
            (Config.TEMP_DIR / "processing").mkdir(exist_ok=True)
            logger.info("🧹 Emergency cleanup complete")


# Singleton instance
downloader = Downloader()
