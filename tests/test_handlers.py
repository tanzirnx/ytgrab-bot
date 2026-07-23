"""
YTGrab Bot - Handler Tests (Unit)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from handlers.download_handler import extract_url


class TestExtractUrl:
    """Test URL extraction from messages."""

    def test_youtube_url(self):
        text = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_url(text) == text

    def test_youtu_be_url(self):
        text = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_url(text) == text

    def test_url_in_sentence(self):
        text = "Check this out https://youtube.com/watch?v=xyz isn't it great?"
        url = extract_url(text)
        assert "youtube.com" in url

    def test_no_url(self):
        text = "Just a regular message with no links"
        assert extract_url(text) is None

    def test_empty_text(self):
        assert extract_url("") is None
        assert extract_url(None) is None

    def test_multiple_urls(self):
        text = "https://youtube.com/watch?v=a and https://youtu.be/b"
        url = extract_url(text)
        assert url is not None  # Should return first one

    def test_url_with_trailing_punctuation(self):
        text = "https://youtube.com/watch?v=xyz."
        url = extract_url(text)
        assert url is not None
        assert not url.endswith(".")

    def test_shorts_url(self):
        text = "https://youtube.com/shorts/abc123"
        url = extract_url(text)
        assert "shorts" in url

    def test_tiktok_url(self):
        text = "https://www.tiktok.com/@user/video/123456"
        url = extract_url(text)
        assert "tiktok" in url

    def test_instagram_url(self):
        text = "https://www.instagram.com/reel/abc123/"
        url = extract_url(text)
        assert "instagram" in url
