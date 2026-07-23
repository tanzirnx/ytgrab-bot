"""
YTGrab Bot - Validator Tests
"""

import pytest
from utils.validators import Validators


class TestURLValidation:
    """Test URL validation functions."""

    def test_is_valid_url_with_valid(self, valid_urls):
        for url in valid_urls:
            assert Validators.is_valid_url(url), f"Should be valid: {url}"

    def test_is_valid_url_with_invalid(self, invalid_urls):
        for url in invalid_urls:
            if url:
                assert not Validators.is_valid_url(url), f"Should be invalid: {url}"

    def test_extract_url_from_text(self):
        text = "Check this out https://youtube.com/watch?v=xyz cool right?"
        url = Validators.extract_url(text)
        assert url == "https://youtube.com/watch?v=xyz"

    def test_extract_url_no_url(self):
        text = "No links here just text"
        url = Validators.extract_url(text)
        assert url is None

    def test_extract_all_urls(self):
        text = "url1: https://youtube.com/watch?v=a and url2: https://youtu.be/b"
        urls = Validators.extract_all_urls(text)
        assert len(urls) == 2

    def test_is_youtube_url(self):
        assert Validators.is_youtube_url("https://www.youtube.com/watch?v=xyz")
        assert Validators.is_youtube_url("https://youtu.be/xyz")
        assert Validators.is_youtube_url("https://youtube.com/shorts/xyz")
        assert not Validators.is_youtube_url("https://vimeo.com/123")

    def test_is_youtube_playlist(self):
        assert Validators.is_youtube_playlist("https://youtube.com/playlist?list=PLxyz")
        assert not Validators.is_youtube_playlist("https://youtube.com/watch?v=xyz")

    def test_extract_video_id(self):
        assert Validators.extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert Validators.extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_is_safe_url(self):
        safe, msg = Validators.is_safe_url("https://youtube.com/watch?v=xyz")
        assert safe is True

        safe, msg = Validators.is_safe_url("http://localhost/admin")
        assert safe is False

        safe, msg = Validators.is_safe_url("ftp://evil.com/file")
        assert safe is False

    def test_sanitize_filename(self):
        assert Validators.sanitize_filename('video: "test" <file>') == "video_test_file"
        assert Validators.sanitize_filename("a" * 300) == "a" * 200
        assert Validators.sanitize_filename("") == "download"
        assert Validators.sanitize_filename("...") == "download"

    def test_parse_time_range(self):
        start, end = Validators.parse_time_range("01:20-02:45")
        assert start == "01:20"
        assert end == "02:45"

        start, end = Validators.parse_time_range("80-165")
        assert start == "80"
        assert end == "165"

        start, end = Validators.parse_time_range("invalid")
        assert start is None
        assert end is None

    def test_parse_playlist_range(self):
        assert Validators.parse_playlist_range("1-10") == (1, 10)
        assert Validators.parse_playlist_range("5-15") == (5, 15)
        assert Validators.parse_playlist_range("invalid") == (1, 10)

    def test_is_valid_bitrate(self):
        assert Validators.is_valid_bitrate(320)
        assert Validators.is_valid_bitrate(128)
        assert not Validators.is_valid_bitrate(999)
        assert not Validators.is_valid_bitrate(0)

    def test_is_valid_resolution(self):
        assert Validators.is_valid_resolution("1080")
        assert Validators.is_valid_resolution("720")
        assert Validators.is_valid_resolution("best")
        assert not Validators.is_valid_resolution("9999")

    def test_is_valid_format(self):
        assert Validators.is_valid_format("mp3")
        assert Validators.is_valid_format("mp4")
        assert Validators.is_valid_format("flac")
        assert not Validators.is_valid_format("exe")
        assert not Validators.is_valid_format("pdf")
