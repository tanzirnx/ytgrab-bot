"""
YTGrab Bot - Test Configuration
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_youtube_url():
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_playlist_url():
    return "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"


@pytest.fixture
def sample_shorts_url():
    return "https://www.youtube.com/shorts/dQw4w9WgXcQ"


@pytest.fixture
def invalid_urls():
    return [
        "not a url",
        "ftp://invalid.com/file",
        "javascript:alert(1)",
        "http://localhost/admin",
        "http://127.0.0.1/secret",
        "",
        None,
    ]


@pytest.fixture
def valid_urls():
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://youtube.com/shorts/abc123",
        "https://soundcloud.com/artist/track",
        "https://twitter.com/user/status/123456",
        "https://www.instagram.com/reel/abc123/",
        "https://vimeo.com/123456789",
    ]
