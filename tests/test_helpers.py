"""
YTGrab Bot - Helper Tests
"""

import pytest
from utils.helpers import Helpers


class TestFormatDuration:
    def test_zero(self):
        assert Helpers.format_duration(0) == "0:00"

    def test_seconds(self):
        assert Helpers.format_duration(45) == "0:45"

    def test_minutes(self):
        assert Helpers.format_duration(125) == "2:05"

    def test_hours(self):
        assert Helpers.format_duration(3661) == "1:01:01"

    def test_negative(self):
        assert Helpers.format_duration(-5) == "0:00"

    def test_none(self):
        assert Helpers.format_duration(None) == "0:00"


class TestFormatFilesize:
    def test_bytes(self):
        assert Helpers.format_filesize(500) == "500.0 B"

    def test_kilobytes(self):
        assert Helpers.format_filesize(1536) == "1.5 KB"

    def test_megabytes(self):
        assert Helpers.format_filesize(5 * 1024 * 1024) == "5.0 MB"

    def test_gigabytes(self):
        assert Helpers.format_filesize(2 * 1024 * 1024 * 1024) == "2.0 GB"

    def test_zero(self):
        assert Helpers.format_filesize(0) == "Unknown"

    def test_negative(self):
        assert Helpers.format_filesize(-1) == "Unknown"


class TestFormatNumber:
    def test_small(self):
        assert Helpers.format_number(999) == "999"

    def test_thousands(self):
        assert Helpers.format_number(1500) == "1.5K"

    def test_millions(self):
        assert Helpers.format_number(2500000) == "2.5M"

    def test_billions(self):
        assert Helpers.format_number(1200000000) == "1.2B"

    def test_none(self):
        assert Helpers.format_number(None) == "0"


class TestProgressBar:
    def test_zero(self):
        bar = Helpers.progress_bar(0)
        assert "░" in bar
        assert "━" not in bar

    def test_half(self):
        bar = Helpers.progress_bar(50)
        assert "━" in bar
        assert "░" in bar

    def test_full(self):
        bar = Helpers.progress_bar(100)
        assert "░" not in bar

    def test_over_100(self):
        bar = Helpers.progress_bar(150)
        assert "░" not in bar


class TestEscapeHtml:
    def test_special_chars(self):
        assert Helpers.escape_html("<script>alert('xss')</script>") == "&lt;script&gt;alert('xss')&lt;/script&gt;"

    def test_ampersand(self):
        assert Helpers.escape_html("Tom & Jerry") == "Tom &amp; Jerry"

    def test_empty(self):
        assert Helpers.escape_html("") == ""

    def test_none(self):
        assert Helpers.escape_html(None) == ""


class TestTruncate:
    def test_short_text(self):
        assert Helpers.truncate("hello", 100) == "hello"

    def test_long_text(self):
        text = "a" * 5000
        result = Helpers.truncate(text, 4000)
        assert len(result) == 4000
        assert result.endswith("...")

    def test_empty(self):
        assert Helpers.truncate("", 100) == ""

    def test_none(self):
        assert Helpers.truncate(None, 100) == ""
