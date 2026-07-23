"""
YTGrab Bot - Metadata Service (Phase 3)
Extracts detailed metadata, comments, and structured info.
"""

import asyncio
from typing import Optional
from loguru import logger

import yt_dlp

from config import Config


class MetadataService:
    """Extracts and structures media metadata."""

    async def extract_full_metadata(self, url: str) -> Optional[dict]:
        """Extract complete metadata as a dictionary."""
        def _extract():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                "writeinfojson": False,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, _extract)

            if not data:
                return None

            # Structure the metadata
            metadata = {
                "id": data.get("id"),
                "title": data.get("title"),
                "description": data.get("description"),
                "duration": data.get("duration"),
                "duration_string": data.get("duration_string"),
                "uploader": data.get("uploader"),
                "uploader_id": data.get("uploader_id"),
                "uploader_url": data.get("uploader_url"),
                "channel": data.get("channel"),
                "channel_id": data.get("channel_id"),
                "channel_url": data.get("channel_url"),
                "channel_follower_count": data.get("channel_follower_count"),
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "comment_count": data.get("comment_count"),
                "upload_date": data.get("upload_date"),
                "release_date": data.get("release_date"),
                "thumbnail": data.get("thumbnail"),
                "webpage_url": data.get("webpage_url"),
                "extractor": data.get("extractor"),
                "extractor_key": data.get("extractor_key"),
                "is_live": data.get("is_live"),
                "was_live": data.get("was_live"),
                "live_status": data.get("live_status"),
                "age_limit": data.get("age_limit"),
                "categories": data.get("categories"),
                "tags": data.get("tags"),
                "chapters": data.get("chapters"),
                "subtitles_available": list(data.get("subtitles", {}).keys()),
                "auto_captions_available": list(data.get("automatic_captions", {}).keys())[:20],
                "formats_count": len(data.get("formats", [])),
                "requested_formats": data.get("requested_formats"),
            }

            # Add format summary
            formats_summary = []
            for f in data.get("formats", [])[:20]:
                formats_summary.append({
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "height": f.get("height"),
                    "width": f.get("width"),
                    "fps": f.get("fps"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "filesize": f.get("filesize"),
                    "tbr": f.get("tbr"),
                })
            metadata["formats_sample"] = formats_summary

            return metadata

        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return None

    async def get_comments(self, url: str, max_comments: int = 10) -> list:
        """Extract top comments from a video."""
        def _extract():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                "getcomments": True,
                "extractor_args": {
                    "youtube": {
                        "max_comments": [str(max_comments), "0", "0", "0"],
                    }
                },
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, _extract)

            if not data or not data.get("comments"):
                return []

            comments = []
            for comment in data.get("comments", [])[:max_comments]:
                comments.append({
                    "author": comment.get("author", "Unknown"),
                    "author_id": comment.get("author_id"),
                    "text": comment.get("text", ""),
                    "like_count": comment.get("like_count", 0),
                    "timestamp": comment.get("timestamp"),
                    "is_favorited": comment.get("is_favorited", False),
                })

            # Sort by likes
            comments.sort(key=lambda x: x.get("like_count", 0), reverse=True)
            return comments

        except Exception as e:
            logger.error(f"Comments extraction error: {e}")
            return []

    async def get_chapters(self, url: str) -> list:
        """Extract chapter information."""
        def _extract():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, _extract)
            return data.get("chapters", []) if data else []
        except Exception:
            return []


# Singleton
metadata_service = MetadataService()
