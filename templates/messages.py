"""
YTGrab Bot - Message Templates
All bot messages in one place for easy management.
"""


class Messages:
    """All bot message templates."""

    # ─── Welcome / Start ────────────────────────────────────

    WELCOME = """
🎬 <b>Welcome to YTGrab Bot!</b>

👋 Hey {name}! I'm your personal media downloader.

📥 I can download <b>audio & video</b> from:
  • YouTube (Videos, Shorts, Live, Music)
  • TikTok, Instagram, Twitter/X
  • SoundCloud, Facebook, Vimeo
  • And <b>1000+ websites!</b>

🚀 <b>How to use:</b>
  Just paste any video/audio link and I'll handle the rest!

⚡ <b>Quick Commands:</b>
  /mp3 <url> → Download audio
  /mp4 <url> → Download video
  /info <url> → Get video info
  /search <query> → Search YouTube
  /help → All commands

⚠️ <i>Free forever. No ads. No registration.</i>
"""

    HELP = """
📖 <b>YTGrab Bot - Help Guide</b>

━━━━━━━━━━━━━━━━━━━━━━━

🎵 <b>Audio Commands:</b>
  /mp3 <url> - Download as MP3
  /m4a <url> - Download as M4A
  /flac <url> - Download as FLAC
  /ogg <url> - Download as OGG
  /wav <url> - Download as WAV

🎬 <b>Video Commands:</b>
  /mp4 <url> - Download as MP4
  /webm <url> - Download as WEBM
  /best <url> - Best quality
  /worst <url> - Smallest size

📋 <b>Info & Extras:</b>
  /info <url> - Video information
  /thumb <url> - Download thumbnail
  /subs <url> - Download subtitles
  /search <query> - Search YouTube

⚙️ <b>Settings:</b>
  /settings - Open settings menu
  /setquality <res> - Default quality
  /setformat <fmt> - Default format
  /reset - Reset all settings

📊 <b>Other:</b>
  /ping - Bot response time
  /version - Bot version info
  /faq - Common questions

━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Tip:</b> Just paste any URL directly!
No command needed. I'll detect it automatically.
"""

    FAQ = """
❓ <b>Frequently Asked Questions</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>Q: Is this bot free?</b>
A: Yes! 100% free forever. No ads, no premium.

<b>Q: What's the max file size?</b>
A: Up to 2GB per file.

<b>Q: Why is my download slow?</b>
A: Depends on server bandwidth & video source.

<b>Q: Can I download playlists?</b>
A: Yes! Up to 100 videos per playlist.

<b>Q: Is it legal?</b>
A: For personal use, generally yes. Check local laws.

<b>Q: Why can't I download this video?</b>
A: It may be private, age-restricted, or region-locked.

<b>Q: How do I report a bug?</b>
A: Use /report or contact @YTGrabDownBot

━━━━━━━━━━━━━━━━━━━━━━━
"""

    FEATURES = """
🎬 <b>What Can I Do?</b>

━━━━━━━━━━━━━━━━━━━━━━━

🎵 <b>Audio Download</b>
  MP3, M4A, FLAC, OGG, WAV, OPUS
  Up to 320kbps quality

🎬 <b>Video Download</b>
  MP4, WEBM, MKV
  144p to 4K (2160p)

📋 <b>Playlist Support</b>
  Download up to 100 videos at once

📝 <b>Subtitles</b>
  Download in any language (SRT, VTT)

🖼 <b>Thumbnails</b>
  HD thumbnails in JPG/PNG

🔍 <b>Search</b>
  Search YouTube directly from bot

🌐 <b>1000+ Websites</b>
  YouTube, TikTok, Instagram, Twitter,
  SoundCloud, Facebook, Vimeo & more!

⚡ <b>Smart Detection</b>
  Just paste a link - no commands needed!

━━━━━━━━━━━━━━━━━━━━━━━
"""

    HOW_TO = """
📖 <b>How to Use YTGrab Bot</b>

━━━━━━━━━━━━━━━━━━━━━━━

<b>Method 1: Just Paste a Link</b>
1️⃣ Copy any YouTube/media URL
2️⃣ Paste it here in chat
3️⃣ Choose Audio or Video
4️⃣ Select quality/format
5️⃣ Receive your file! 🎉

<b>Method 2: Use Commands</b>
• /mp3 https://youtube.com/watch?v=xyz
• /mp4 https://youtube.com/watch?v=xyz
• /best https://youtube.com/watch?v=xyz

<b>Method 3: Search</b>
• /search lofi hip hop
• Click on a result to download

━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Examples:</b>
<code>https://youtube.com/watch?v=dQw4w9WgXcQ</code>
<code>https://youtu.be/dQw4w9WgXcQ</code>
<code>https://youtube.com/shorts/xyz</code>

👇 Try it now! Paste a link below.
"""

    # ─── Download Messages ──────────────────────────────────

    DETECTING_URL = "🔍 <i>Detecting media...</i>"

    VIDEO_INFO = """
🎬 <b>{title}</b>

👤 <b>Channel:</b> {uploader}
⏱ <b>Duration:</b> {duration}
👁 <b>Views:</b> {views}
👍 <b>Likes:</b> {likes}
🌐 <b>Platform:</b> {platform}

━━━━━━━━━━━━━━━━━━━━━━━
⬇️ Choose what to download:
"""

    DOWNLOADING_AUDIO = """
⬇️ <b>Downloading Audio...</b>

🎵 {title}
📊 Format: {format} | {bitrate}kbps

{progress_bar} {percent}%
⚡ Speed: {speed}
⏱ ETA: {eta}
📦 Size: {size}
"""

    DOWNLOADING_VIDEO = """
⬇️ <b>Downloading Video...</b>

🎬 {title}
📊 Quality: {resolution} | Format: {format}

{progress_bar} {percent}%
⚡ Speed: {speed}
⏱ ETA: {eta}
📦 Size: {size}
"""

    DOWNLOAD_COMPLETE = """
✅ <b>Download Complete!</b>

📄 {title}
📦 Size: {size}
⏱ Duration: {duration}

🎉 Enjoy!
"""

    UPLOADING = "📤 <i>Uploading to Telegram... {percent}%</i>"

    # ─── Error Messages ─────────────────────────────────────

    ERROR_INVALID_URL = """
❌ <b>Invalid URL</b>

I couldn't recognize that link. Please paste a valid URL from:
• YouTube, TikTok, Instagram, Twitter
• SoundCloud, Facebook, Vimeo, Reddit
• Or any of 1000+ supported sites

💡 Example: <code>https://youtube.com/watch?v=dQw4w9WgXcQ</code>
"""

    ERROR_NOT_FOUND = """
❌ <b>Video Not Found</b>

This video may have been:
• Deleted or removed
• Made private by the uploader
• Never existed (broken link)

💡 Try searching with /search instead.
"""

    ERROR_PRIVATE = """
🔒 <b>Private Video</b>

This video is set to private by the uploader.
I cannot download private videos.
"""

    ERROR_AGE_RESTRICTED = """
⚠️ <b>Age-Restricted Content</b>

This video has age restrictions and cannot
be downloaded without authentication.
"""

    ERROR_COPYRIGHT = """
❌ <b>Copyright Blocked</b>

This video is blocked due to copyright claims
in the bot's server region.
"""

    ERROR_FILE_TOO_LARGE = """
⚠️ <b>File Too Large</b>

The file size ({size}) exceeds the maximum limit ({limit}).

💡 Try:
• Lower video quality (/worst)
• Download audio only (/mp3)
• Download a shorter clip
"""

    ERROR_DOWNLOAD_FAILED = """
❌ <b>Download Failed</b>

Something went wrong while downloading.
This might be due to:
• Server connectivity issues
• Video is temporarily unavailable
• Format not available

🔄 Please try again in a few moments.
"""

    ERROR_RATE_LIMIT = """
⏳ <b>Rate Limit Reached</b>

You've made too many requests.
Please wait <b>{wait_time}</b> before trying again.

📊 Your limit: {limit} downloads/day
"""

    ERROR_BANNED = """
🚫 <b>Access Denied</b>

You have been banned from using this bot.
Contact the admin if you think this is a mistake.
"""

    # ─── Settings Messages ──────────────────────────────────

    SETTINGS_UPDATED = "✅ <b>Setting Updated!</b>\n\n{key}: {value}"

    SETTINGS_RESET = "🔄 <b>All settings reset to defaults.</b>"

    SETTINGS_CURRENT = """
⚙️ <b>Your Current Settings</b>

━━━━━━━━━━━━━━━━━━━━━━━
🎵 Default Format: <b>{format}</b>
📺 Default Quality: <b>{quality}p</b>
🎧 Audio Bitrate: <b>{bitrate}kbps</b>
🖼 Auto Thumbnail: <b>{thumbnail}</b>
📝 Auto Subtitles: <b>{subtitles}</b>
🔔 Notifications: <b>{notifications}</b>
━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ─── Admin Messages ─────────────────────────────────────

    ADMIN_DASHBOARD = """
📊 <b>YTGrab Bot Dashboard</b>

━━━━━━━━━━━━━━━━━━━━━━━
👥 Total Users: <b>{total_users}</b>
📥 Downloads Today: <b>{downloads_today}</b>
📥 Downloads Total: <b>{total_downloads}</b>
💾 Total Data: <b>{total_data} MB</b>
⏱ Uptime: <b>{uptime}</b>
🔄 yt-dlp: <b>{ytdlp_version}</b>
🐍 Python: <b>{python_version}</b>
━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ─── Utility ────────────────────────────────────────────

    PING_RESPONSE = "🏓 <b>Pong!</b> Response time: {ms}ms"

    VERSION_INFO = """
🤖 <b>YTGrab Bot v1.0.0</b>

📦 yt-dlp: {ytdlp_version}
🐍 Python: {python_version}
📅 Built: July 2026
👤 Bot: @YTGrabDownBot

⚡ 100% Free & Open Source
"""

    MAINTENANCE_MODE = """
🔧 <b>Under Maintenance</b>

The bot is currently under maintenance.
Please try again in a few minutes.

Sorry for the inconvenience! 🙏
"""

    # ─── Helper Methods ─────────────────────────────────────

    @staticmethod
    def format_number(num: int) -> str:
        """Format large numbers with K/M/B suffix."""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

    @staticmethod
    def format_filesize(bytes: int) -> str:
        """Format file size in human-readable format."""
        if bytes <= 0:
            return "Unknown"
        units = ["B", "KB", "MB", "GB"]
        unit_idx = 0
        size = float(bytes)
        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1
        return f"{size:.1f} {units[unit_idx]}"

    @staticmethod
    def progress_bar(percent: float, length: int = 20) -> str:
        """Generate text progress bar."""
        filled = int(length * percent / 100)
        bar = "━" * filled + "░" * (length - filled)
        return f"[{bar}]"
