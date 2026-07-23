"""
YTGrab Bot - Constants
"""

# ─── Bot Info ───────────────────────────────────────────────
BOT_VERSION = "1.0.0"
BOT_PHASE = "Phase 2"
BOT_NAME = "YTGrab Bot"
BOT_USERNAME = "@YTGrabDownBot"

# ─── Callback Data Prefixes ────────────────────────────────
CB_ACTION_AUDIO = "action_audio"
CB_ACTION_VIDEO = "action_video"
CB_ACTION_INFO = "action_info"
CB_ACTION_THUMB = "action_thumb"
CB_ACTION_SUBS = "action_subs"
CB_ACTION_OPTIONS = "action_options"
CB_ACTION_MENU = "action_menu"
CB_DL_PREFIX = "dl_"
CB_DL_VID_PREFIX = "dl_vid_"
CB_DL_SUB_PREFIX = "dl_sub_"
CB_SEARCH_DL = "search_dl"
CB_BACK_START = "back_start"
CB_MENU_PREFIX = "menu_"
CB_SET_PREFIX = "set_"
CB_PREF_PREFIX = "pref_"
CB_PL_PREFIX = "pl_"
CB_ADMIN_PREFIX = "admin_"
CB_QUEUE_PREFIX = "queue_"

# ─── File Extensions ───────────────────────────────────────
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".opus", ".aac", ".wma"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".json3", ".txt"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz"}

# ─── Blocked File Extensions (security) ────────────────────
BLOCKED_EXTENSIONS = {
    ".exe", ".sh", ".bat", ".cmd", ".com", ".msi", ".scr",
    ".pif", ".vbs", ".js", ".jar", ".apk", ".dll", ".sys",
}

# ─── Platform Display Names ────────────────────────────────
PLATFORM_NAMES = {
    "youtube": "YouTube",
    "soundcloud": "SoundCloud",
    "twitter": "Twitter/X",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "vimeo": "Vimeo",
    "reddit": "Reddit",
    "dailymotion": "Dailymotion",
    "twitch": "Twitch",
    "pinterest": "Pinterest",
    "tumblr": "Tumblr",
    "bilibili": "Bilibili",
}

# ─── Language Codes ────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "🇬🇧 English",
    "hi": "🇮🇳 Hindi",
    "es": "🇪🇸 Spanish",
    "ar": "🇸🇦 Arabic",
    "fr": "🇫🇷 French",
    "pt": "🇧🇷 Portuguese",
    "ru": "🇷🇺 Russian",
    "ja": "🇯🇵 Japanese",
    "ko": "🇰🇷 Korean",
    "zh": "🇨🇳 Chinese",
}

# ─── Emoji Constants ───────────────────────────────────────
EMOJI_AUDIO = "🎵"
EMOJI_VIDEO = "🎬"
EMOJI_DOWNLOAD = "⬇️"
EMOJI_UPLOAD = "📤"
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "📋"
EMOJI_SETTINGS = "⚙️"
EMOJI_SEARCH = "🔍"
EMOJI_THUMB = "🖼"
EMOJI_SUBS = "📝"
EMOJI_PLAYLIST = "📁"
EMOJI_QUEUE = "📊"
EMOJI_LIVE = "🔴"
EMOJI_LOCK = "🔒"
EMOJI_BAN = "🚫"
EMOJI_STAR = "⭐"
EMOJI_FIRE = "🔥"
EMOJI_ROCKET = "🚀"
