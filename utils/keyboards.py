"""
YTGrab Bot - Inline Keyboard Builder
All inline keyboards for bot interactions.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    """Builder for all inline keyboards."""

    # ─── Start / Welcome ────────────────────────────────────

    @staticmethod
    def start_menu() -> InlineKeyboardMarkup:
        """Main menu after /start."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎬 What can I do?", callback_data="menu_features"),
                InlineKeyboardButton("📖 How to use?", callback_data="menu_howto"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
                InlineKeyboardButton("❓ FAQ", callback_data="menu_faq"),
            ],
            [
                InlineKeyboardButton("⭐ Rate Bot", url="https://t.me/YTGrabDownBot"),
                InlineKeyboardButton("📢 Channel", url="https://t.me/YTGrabDownBot"),
            ],
        ])

    @staticmethod
    def back_to_start() -> InlineKeyboardMarkup:
        """Back to main menu."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_start")]
        ])

    # ─── Media Action Menu (after URL detection) ────────────

    @staticmethod
    def media_action_menu(url: str) -> InlineKeyboardMarkup:
        """Main action menu after URL is detected."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Audio", callback_data=f"action_audio|{url}"),
                InlineKeyboardButton("🎬 Video", callback_data=f"action_video|{url}"),
            ],
            [
                InlineKeyboardButton("📋 Info", callback_data=f"action_info|{url}"),
                InlineKeyboardButton("🖼 Thumbnail", callback_data=f"action_thumb|{url}"),
            ],
            [
                InlineKeyboardButton("📝 Subtitles", callback_data=f"action_subs|{url}"),
                InlineKeyboardButton("⚙️ Options", callback_data=f"action_options|{url}"),
            ],
        ])

    # ─── Audio Format Selection ─────────────────────────────

    @staticmethod
    def audio_format_menu(url: str) -> InlineKeyboardMarkup:
        """Audio format selection."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 MP3 128k", callback_data=f"dl_mp3_128|{url}"),
                InlineKeyboardButton("🎵 MP3 320k", callback_data=f"dl_mp3_320|{url}"),
            ],
            [
                InlineKeyboardButton("🎶 M4A", callback_data=f"dl_m4a_256|{url}"),
                InlineKeyboardButton("🎶 FLAC", callback_data=f"dl_flac_0|{url}"),
            ],
            [
                InlineKeyboardButton("🎶 OGG", callback_data=f"dl_ogg_256|{url}"),
                InlineKeyboardButton("🎶 WAV", callback_data=f"dl_wav_0|{url}"),
            ],
            [
                InlineKeyboardButton("🎶 OPUS", callback_data=f"dl_opus_128|{url}"),
                InlineKeyboardButton("✨ Best", callback_data=f"dl_mp3_320|{url}"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data=f"action_menu|{url}"),
            ],
        ])

    # ─── Video Quality Selection ────────────────────────────

    @staticmethod
    def video_quality_menu(url: str) -> InlineKeyboardMarkup:
        """Video quality selection."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📺 2160p (4K)", callback_data=f"dl_vid_2160|{url}"),
                InlineKeyboardButton("📺 1440p (2K)", callback_data=f"dl_vid_1440|{url}"),
            ],
            [
                InlineKeyboardButton("📺 1080p (FHD)", callback_data=f"dl_vid_1080|{url}"),
                InlineKeyboardButton("📺 720p (HD)", callback_data=f"dl_vid_720|{url}"),
            ],
            [
                InlineKeyboardButton("📺 480p", callback_data=f"dl_vid_480|{url}"),
                InlineKeyboardButton("📺 360p", callback_data=f"dl_vid_360|{url}"),
            ],
            [
                InlineKeyboardButton("📺 240p", callback_data=f"dl_vid_240|{url}"),
                InlineKeyboardButton("📱 144p", callback_data=f"dl_vid_144|{url}"),
            ],
            [
                InlineKeyboardButton("✨ Best Quality", callback_data=f"dl_vid_best|{url}"),
                InlineKeyboardButton("💾 Smallest", callback_data=f"dl_vid_worst|{url}"),
            ],
            [
                InlineKeyboardButton("🎵 Audio Only", callback_data=f"action_audio|{url}"),
                InlineKeyboardButton("⬅️ Back", callback_data=f"action_menu|{url}"),
            ],
        ])

    # ─── Subtitle Language Selection ────────────────────────

    @staticmethod
    def subtitle_lang_menu(url: str, languages: list = None) -> InlineKeyboardMarkup:
        """Subtitle language selection."""
        if not languages:
            languages = ["en", "hi", "es", "fr", "ar", "pt", "ru", "ja", "ko", "zh"]

        buttons = []
        row = []
        for lang in languages[:12]:
            row.append(
                InlineKeyboardButton(
                    f"📝 {lang.upper()}",
                    callback_data=f"dl_sub_{lang}|{url}"
                )
            )
            if len(row) == 4:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data=f"action_menu|{url}")
        ])

        return InlineKeyboardMarkup(buttons)

    # ─── Settings Menu ──────────────────────────────────────

    @staticmethod
    def settings_menu(current: dict = None) -> InlineKeyboardMarkup:
        """User settings menu."""
        current = current or {}
        fmt = current.get("default_format", "mp3")
        quality = current.get("default_video_resolution", "1080")
        thumb = "✅" if current.get("auto_thumbnail", True) else "❌"
        subs = "✅" if current.get("auto_subtitles", False) else "❌"
        notify = "✅" if current.get("notifications", True) else "❌"

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"🎵 Format: {fmt.upper()}", callback_data="set_format"),
                InlineKeyboardButton(f"📺 Quality: {quality}p", callback_data="set_quality"),
            ],
            [
                InlineKeyboardButton(f"🖼 Thumbnail: {thumb}", callback_data="set_thumb"),
                InlineKeyboardButton(f"📝 Subtitles: {subs}", callback_data="set_subs"),
            ],
            [
                InlineKeyboardButton(f"🔔 Notify: {notify}", callback_data="set_notify"),
                InlineKeyboardButton("🔄 Reset All", callback_data="set_reset"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_start"),
            ],
        ])

    @staticmethod
    def format_selection() -> InlineKeyboardMarkup:
        """Default format selection."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 MP3", callback_data="pref_format_mp3"),
                InlineKeyboardButton("🎶 M4A", callback_data="pref_format_m4a"),
            ],
            [
                InlineKeyboardButton("🎬 MP4", callback_data="pref_format_mp4"),
                InlineKeyboardButton("🎬 WEBM", callback_data="pref_format_webm"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="menu_settings"),
            ],
        ])

    @staticmethod
    def quality_selection() -> InlineKeyboardMarkup:
        """Default quality selection."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("2160p", callback_data="pref_quality_2160"),
                InlineKeyboardButton("1440p", callback_data="pref_quality_1440"),
                InlineKeyboardButton("1080p", callback_data="pref_quality_1080"),
            ],
            [
                InlineKeyboardButton("720p", callback_data="pref_quality_720"),
                InlineKeyboardButton("480p", callback_data="pref_quality_480"),
                InlineKeyboardButton("360p", callback_data="pref_quality_360"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="menu_settings"),
            ],
        ])

    # ─── Search Results ─────────────────────────────────────

    @staticmethod
    def search_results(results: list) -> InlineKeyboardMarkup:
        """Search results with download buttons."""
        buttons = []
        for i, result in enumerate(results[:5]):
            title = result.get("title", "Unknown")[:40]
            duration = result.get("duration_str", "")
            buttons.append([
                InlineKeyboardButton(
                    f"{'🔴' if result.get('is_live') else '🎵'} {title} ({duration})",
                    callback_data=f"search_dl|{result.get('url', '')}"
                )
            ])
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="back_start")
        ])
        return InlineKeyboardMarkup(buttons)

    # ─── Confirm / Cancel ───────────────────────────────────

    @staticmethod
    def confirm_cancel(action: str) -> InlineKeyboardMarkup:
        """Generic confirm/cancel."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ No", callback_data="back_start"),
            ]
        ])

    # ─── Error Recovery ─────────────────────────────────────

    @staticmethod
    def error_retry(url: str) -> InlineKeyboardMarkup:
        """Retry after error."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Retry", callback_data=f"action_menu|{url}"),
                InlineKeyboardButton("⬅️ Cancel", callback_data="back_start"),
            ]
        ])
