"""
YTGrab Bot - SponsorBlock Service (Phase 3)
Integrates with SponsorBlock API to skip sponsor segments.
"""

import asyncio
import aiohttp
from typing import Optional
from loguru import logger

from config import Config


class SponsorBlockService:
    """SponsorBlock API integration."""

    API_URL = "https://sponsor.ajay.app/api/skipSegments"

    CATEGORIES = [
        "sponsor",
        "selfpromo",
        "interaction",
        "intro",
        "outro",
        "preview",
        "filler",
        "music_offtopic",
    ]

    async def get_segments(self, video_id: str, categories: list = None) -> list:
        """Get sponsor segments for a video."""
        if not categories:
            categories = ["sponsor", "selfpromo", "interaction"]

        try:
            params = {
                "videoID": video_id,
                "categories": str(categories).replace("'", '"'),
                "actionType": "skip",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.API_URL, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        segments = []
                        for item in data:
                            segment = item.get("segment", [])
                            if len(segment) == 2:
                                segments.append({
                                    "start": segment[0],
                                    "end": segment[1],
                                    "category": item.get("category", "unknown"),
                                    "duration": segment[1] - segment[0],
                                })
                        logger.info(f"🛡️ SponsorBlock: {len(segments)} segments for {video_id}")
                        return segments
                    elif resp.status == 404:
                        return []  # No segments
                    else:
                        logger.warning(f"SponsorBlock API returned {resp.status}")
                        return []

        except asyncio.TimeoutError:
            logger.warning("SponsorBlock API timeout")
            return []
        except Exception as e:
            logger.error(f"SponsorBlock error: {e}")
            return []

    def get_ffmpeg_filter(self, segments: list) -> Optional[str]:
        """Generate FFmpeg filter to remove sponsor segments."""
        if not segments:
            return None

        # Sort by start time
        segments.sort(key=lambda x: x["start"])

        # Build select filter
        # This creates a complex filter that removes segments
        conditions = []
        for seg in segments:
            conditions.append(f"between(t,{seg['start']:.3f},{seg['end']:.3f})")

        # Invert: select everything EXCEPT sponsor segments
        filter_str = "select='not(" + "+".join(conditions) + ")'"
        return filter_str

    def get_total_skip_duration(self, segments: list) -> float:
        """Get total duration that would be skipped."""
        return sum(seg.get("duration", 0) for seg in segments)

    async def get_ytdlp_args(self, video_id: str) -> dict:
        """Get yt-dlp arguments for SponsorBlock integration."""
        segments = await self.get_segments(video_id)

        if not segments:
            return {}

        # yt-dlp has built-in SponsorBlock support
        return {
            "postprocessors": [
                {
                    "key": "SponsorBlock",
                    "categories": ["sponsor", "selfpromo", "interaction"],
                },
                {
                    "key": "ModifyChapters",
                    "remove_sponsor_segments": ["sponsor", "selfpromo", "interaction"],
                },
            ],
        }


# Singleton
sponsorblock_service = SponsorBlockService()
