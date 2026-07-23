"""
YTGrab Bot - URL & Input Validators
"""

import re
from urllib.parse import urlparse
from typing import Optional, Tuple
from loguru import logger

from utils.constants import BLOCKED_EXTENSIONS


# ─── URL Patterns ───────────────────────────────────────────

YOUTUBE_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]{11})',
    r'(?:https?://)?(?:www\.)?youtu\.be/([\w-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([\w-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/live/([\w-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([\w-]{11})',
]

YOUTUBE_PLAYLIST_PATTERN = r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([\w-]+)'
YOUTUBE_CHANNEL_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/channel/([\w-]+)',
    r'(?:https?://)?(?:www\.)?youtube\.com/@([\w.-]+)',
    r'(?:https?://)?(?:www\.)?youtube\.com/c/([\w.-]+)',
]

GENERIC_URL_PATTERN = re.compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
    r'(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
    re.IGNORECASE
)


class Validators:
    """Input validation utilities."""

    @staticmethod
    def is_valid_url(text: str) -> bool:
        """Check if text contains a valid URL."""
        return bool(GENERIC_URL_PATTERN.search(text))

    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """Extract first URL from text."""
        match = GENERIC_URL_PATTERN.search(text)
        if match:
            url = match.group(0).rstrip('.,;!?\'"')
            return url
        return None

    @staticmethod
    def extract_all_urls(text: str) -> list:
        """Extract all URLs from text."""
        matches = GENERIC_URL_PATTERN.findall(text)
        return [url.rstrip('.,;!?\'"') for url in matches]

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if URL is a YouTube URL."""
        for pattern in YOUTUBE_PATTERNS:
            if re.search(pattern, url):
                return True
        if YOUTUBE_PLAYLIST_PATTERN and re.search(YOUTUBE_PLAYLIST_PATTERN, url):
            return True
        return False

    @staticmethod
    def is_youtube_playlist(url: str) -> bool:
        """Check if URL is a YouTube playlist."""
        return bool(re.search(YOUTUBE_PLAYLIST_PATTERN, url))

    @staticmethod
    def is_youtube_channel(url: str) -> bool:
        """Check if URL is a YouTube channel."""
        for pattern in YOUTUBE_CHANNEL_PATTERNS:
            if re.search(pattern, url):
                return True
        return False

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        for pattern in YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """Extract YouTube playlist ID."""
        match = re.search(YOUTUBE_PLAYLIST_PATTERN, url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def is_safe_url(url: str) -> Tuple[bool, str]:
        """Validate URL safety."""
        try:
            parsed = urlparse(url)

            # Must be http/https
            if parsed.scheme not in ('http', 'https'):
                return False, "Only HTTP/HTTPS URLs are allowed"

            # Must have a domain
            if not parsed.netloc:
                return False, "Invalid URL: no domain"

            # Block localhost/internal IPs
            blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1', '10.', '192.168.', '172.16.']
            for blocked in blocked_hosts:
                if parsed.netloc.startswith(blocked):
                    return False, "Internal URLs are not allowed"

            # Block dangerous file extensions
            path_lower = parsed.path.lower()
            for ext in BLOCKED_EXTENSIONS:
                if path_lower.endswith(ext):
                    return False, f"Blocked file type: {ext}"

            return True, "OK"

        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 200) -> str:
        """Sanitize a filename by removing illegal characters."""
        # Remove illegal characters
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        name = re.sub(illegal_chars, '_', name)

        # Remove leading/trailing dots and spaces
        name = name.strip('. ')

        # Collapse multiple underscores/spaces
        name = re.sub(r'[_\s]+', '_', name)

        # Truncate
        if len(name) > max_length:
            name = name[:max_length]

        # Fallback
        if not name:
            name = "download"

        return name

    @staticmethod
    def parse_time_range(time_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse time range string like '01:20-02:45' or '80-165'."""
        patterns = [
            # HH:MM:SS-HH:MM:SS
            r'(\d{1,2}:\d{2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2}:\d{2})',
            # MM:SS-MM:SS
            r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})',
            # seconds-seconds
            r'(\d+)\s*[-–]\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                return match.group(1), match.group(2)
        return None, None

    @staticmethod
    def parse_playlist_range(range_str: str) -> Tuple[int, int]:
        """Parse playlist range like '1-10' or '5-15'."""
        match = re.match(r'(\d+)\s*[-–]\s*(\d+)', range_str.strip())
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            return max(1, start), max(start, end)
        return 1, 10  # default

    @staticmethod
    def is_valid_bitrate(bitrate: int) -> bool:
        """Check if bitrate is valid."""
        return bitrate in [64, 96, 128, 160, 192, 256, 320]

    @staticmethod
    def is_valid_resolution(resolution: str) -> bool:
        """Check if resolution is valid."""
        valid = ['144', '240', '360', '480', '720', '1080', '1440', '2160', 'best', 'worst']
        return resolution.lower() in valid

    @staticmethod
    def is_valid_format(fmt: str) -> bool:
        """Check if format is valid."""
        valid = ['mp3', 'm4a', 'flac', 'ogg', 'wav', 'opus', 'aac',
                 'mp4', 'webm', 'mkv', 'avi']
        return fmt.lower() in valid
