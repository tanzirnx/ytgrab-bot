"""
YTGrab Bot - Downloader Tests
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from services.downloader import Downloader, DownloadProgress, MediaInfo


class TestDownloaderUtils:
    """Test downloader utility methods."""

    def setup_method(self):
        self.downloader = Downloader()

    def test_format_duration(self):
        assert self.downloader._format_duration(0) == "0:00"
        assert self.downloader._format_duration(65) == "1:05"
        assert self.downloader._format_duration(3661) == "1:01:01"

    def test_format_speed(self):
        assert self.downloader._format_speed(0) == "0 B/s"
        assert self.downloader._format_speed(1024) == "1.0 KB/s"
        assert self.downloader._format_speed(1048576) == "1.0 MB/s"

    def test_format_eta(self):
        assert self.downloader._format_eta(0) == "calculating..."
        assert self.downloader._format_eta(30) == "30s"
        assert self.downloader._format_eta(90) == "1m 30s"

    def test_parse_formats(self):
        formats = [
            {"height": 1080, "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a", "filesize": 100000, "format_id": "137"},
            {"height": 720, "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a", "filesize": 50000, "format_id": "22"},
            {"height": None, "ext": "m4a", "vcodec": "none", "acodec": "mp4a", "filesize": 5000, "format_id": "140"},
        ]
        parsed = self.downloader._parse_formats(formats)
        assert len(parsed) == 2  # Only video formats
        assert parsed[0]["resolution"] == "1080p"
        assert parsed[1]["resolution"] == "720p"


class TestDownloadProgress:
    """Test DownloadProgress dataclass."""

    def test_defaults(self):
        progress = DownloadProgress()
        assert progress.percent == 0.0
        assert progress.status == "downloading"

    def test_custom_values(self):
        progress = DownloadProgress(
            percent=75.5,
            speed="4.2 MB/s",
            eta="0:23",
            downloaded_bytes=75000000,
            total_bytes=100000000,
        )
        assert progress.percent == 75.5
        assert progress.speed == "4.2 MB/s"


class TestMediaInfo:
    """Test MediaInfo dataclass."""

    def test_defaults(self):
        info = MediaInfo()
        assert info.title == ""
        assert info.duration == 0
        assert info.error == ""
        assert info.is_live is False
        assert info.is_playlist is False

    def test_with_values(self):
        info = MediaInfo(
            title="Test Video",
            duration=300,
            uploader="Test Channel",
            views=1000000,
        )
        assert info.title == "Test Video"
        assert info.duration == 300
