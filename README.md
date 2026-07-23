<div align="center">

# 🎬 YTGrab Bot

### Free YouTube & Media Downloader Telegram Bot

**Download audio, video, playlists, subtitles & thumbnails from 1000+ websites — directly in Telegram.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![Telegram](https://img.shields.io/badge/Telegram-@YTGrabDownBot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/YTGrabDownBot)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-powered-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-Free_&_Open_Source-00C853?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-1000+_Websites-FF6D00?style=for-the-badge)](#-supported-platforms)

[![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat-square)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square)]()
[![Commands](https://img.shields.io/badge/Commands-70+-purple?style=flat-square)](#-complete-command-list)
[![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)]()

[**Try the Bot →**](https://t.me/YTGrabDownBot) · [**Features**](#-features) · [**Quick Start**](#-quick-start) · [**Commands**](#-complete-command-list) · [**Deploy**](#-deployment) · [**FAQ**](#-faq)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Platforms](#-supported-platforms)
- [Quick Start](#-quick-start)
- [Complete Command List](#-complete-command-list)
- [Screenshots & Usage](#-screenshots--usage)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Docker](#-docker-deployment)
- [Testing](#-testing)
- [Multi-Language Support](#-multi-language-support)
- [Rate Limiting & Security](#-rate-limiting--security)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Legal Disclaimer](#-legal-disclaimer)
- [Credits](#-credits)
- [Support](#-support)
- [License](#-license)

---

## 🎯 Overview

**YTGrab Bot** is a **100% free**, feature-rich Telegram bot that lets you download media from YouTube and 1000+ websites with zero ads, zero registration, and zero cost.

Just **paste a link** → **choose format** → **receive your file**. That's it!

```
📋 Paste URL → 🎵 Choose Audio/Video → ⚡ Select Quality → 📥 Get File!
```

### Why YTGrab Bot?

| ❌ Web Downloaders | ✅ YTGrab Bot |
|---|---|
| Full of malware & pop-up ads | 100% clean & safe |
| Requires signup/login | Zero registration |
| Limited formats & quality | All formats, up to 4K |
| Slow & unreliable | Fast & stable |
| Doesn't work on mobile | Works everywhere (Telegram) |
| No playlist support | Full playlist support |
| No subtitle download | Subtitles in any language |

---

## ✨ Features

### 🎵 Audio Download
- **Formats:** MP3, M4A, FLAC, OGG, WAV, OPUS, AAC
- **Bitrates:** 64, 128, 192, 256, 320 kbps
- Auto-embed **thumbnail as album art**
- Auto-embed **metadata** (title, artist, ID3 tags)
- Split long audio into **chapters** (`/audiobook`)
- Download audio from **playlists**

### 🎬 Video Download
- **Formats:** MP4, WEBM, MKV
- **Resolutions:** 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, **4K (2160p)**
- Auto-merge best video + best audio streams
- Download **without audio** (`/noaudio`)
- Convert to **GIF** (`/gif`)
- **Time-range clipping** (`/clip 01:20-02:45`)
- Embed subtitles into video
- Embed chapters/timestamps

### 📁 Playlist & Batch
- Download **entire playlists** (up to 100 videos)
- **Select range** (videos 1-10, 11-20, etc.)
- Choose format for all videos
- **Batch download** multiple URLs at once
- Real-time progress tracking per video

### 📝 Subtitles
- Download subtitles in **any language**
- Formats: **SRT, VTT, ASS, JSON3**
- Auto-generated subtitles support
- List all available languages (`/subslist`)
- Set default subtitle language

### 🖼 Thumbnails & Metadata
- Download **HD thumbnails** (JPG, PNG, WEBP)
- Export full **metadata as JSON**
- Get video **description** text
- Get **top comments** with likes
- View **all available formats** (`/format`)

### 🔍 Search & Discovery
- **Search YouTube** directly from bot
- **Trending videos** by country/region
- Download **YouTube Shorts**
- Capture **livestreams**
- Inline result selection with buttons

### ⚙️ User Settings
- Default format & quality preferences
- Auto-thumbnail toggle
- Auto-subtitle toggle
- Custom **filename templates**
- **Multi-language** interface (7 languages)
- Notification preferences

### 👥 Group Chat Support
- Works in **group chats**
- Admin controls (enable/disable bot)
- **Per-user download limits**
- **Silent mode** (responds only when mentioned)
- Group-specific settings

### 🛡️ Privacy & Security
- ❌ **No data logging** — we don't track you
- ❌ **No user history** stored (optional)
- ❌ **No analytics** or tracking
- ✅ Only stores: User ID + Preferences
- ✅ Auto-delete temp files after download
- ✅ Rate limiting & abuse prevention
- ✅ Input sanitization (no command injection)
- ✅ GDPR compliant

### 📊 Admin Dashboard
- Real-time statistics (users, downloads, storage)
- **Broadcast** messages to all users
- **Ban/unban** users
- Set daily download limits
- **Maintenance mode** toggle
- View error logs
- Update yt-dlp remotely
- Restart bot remotely

---

## 🌐 Supported Platforms

YTGrab Bot supports **1000+ websites** via the yt-dlp engine:

| Platform | Content Types |
|----------|--------------|
| 🎬 **YouTube** | Videos, Shorts, Live, Premieres, Music |
| 🎵 **SoundCloud** | Tracks, Playlists, Albums |
| 🐦 **Twitter/X** | Videos, Spaces, GIFs |
| 📸 **Instagram** | Reels, Posts, Stories, IGTV |
| 🎵 **TikTok** | Videos (with/without watermark) |
| 📘 **Facebook** | Videos, Reels, Watch |
| 🎥 **Vimeo** | Videos, Channels |
| 🤖 **Reddit** | Videos, GIFs |
| 📺 **Dailymotion** | Videos |
| 🎮 **Twitch** | Clips, VODs |
| 📌 **Pinterest** | Videos, Pins |
| 📝 **Tumblr** | Videos |
| 📺 **Bilibili** | Videos |
| ➕ **1000+ more** | Any site supported by yt-dlp |

> 💡 **Full list:** https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| FFmpeg | Latest | [ffmpeg.org](https://ffmpeg.org) |
| Telegram Bot Token | — | [@BotFather](https://t.me/BotFather) |

### 1-Minute Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ytgrab-bot.git
cd ytgrab-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
sudo apt install ffmpeg -y      # Ubuntu/Debian
# brew install ffmpeg           # macOS
# choco install ffmpeg          # Windows

# Configure
cp .env.example .env
nano .env                       # Add your BOT_TOKEN & ADMIN_ID

# Run!
python bot.py
```

### Get Your Bot Token

1. Open Telegram → Search **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot`
3. Name: `YTGrab Bot`
4. Username: `YTGrabDownBot`
5. Copy the token: `7123456789:AAH_your_token_here`

### Get Your Admin ID

1. Open Telegram → Search **[@userinfobot](https://t.me/userinfobot)**
2. Send any message → It replies with your ID
3. Use that ID in `.env` as `ADMIN_ID=123456789`

### Verify Installation

```bash
# Run tests
python -m pytest tests/ -v

# Start bot
python bot.py

# You should see:
# 🚀 Starting YTGrab Bot v1.0.0
# 🟢 Bot is now polling for updates...
```

Open Telegram → **@YTGrabDownBot** → Send `/start` → 🎉

---

## 📋 Complete Command List

### 🏠 Primary Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message & menu | `/start` |
| `/help` | Full command list & guide | `/help` |
| `/faq` | Frequently asked questions | `/faq` |
| `/ping` | Check bot response time | `/ping` |
| `/version` | Bot & engine version info | `/version` |

### 🎵 Audio Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/mp3 <url>` | Download as MP3 | `/mp3 https://youtube.com/watch?v=xyz` |
| `/m4a <url>` | Download as M4A | `/m4a <url>` |
| `/flac <url>` | Download as FLAC (lossless) | `/flac <url>` |
| `/ogg <url>` | Download as OGG | `/ogg <url>` |
| `/wav <url>` | Download as WAV | `/wav <url>` |
| `/opus <url>` | Download as OPUS | `/opus <url>` |
| `/aac <url>` | Download as AAC | `/aac <url>` |
| `/audiobook <url>` | Download with chapter splitting | `/audiobook <url>` |

### 🎬 Video Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/mp4 <url>` | Download as MP4 | `/mp4 https://youtube.com/watch?v=xyz` |
| `/webm <url>` | Download as WEBM | `/webm <url>` |
| `/mkv <url>` | Download as MKV | `/mkv <url>` |
| `/best <url>` | Best available quality | `/best <url>` |
| `/worst <url>` | Lowest quality (save data) | `/worst <url>` |
| `/gif <url>` | Convert to GIF (30s) | `/gif <url>` |
| `/clip <url> <range>` | Download time range | `/clip <url> 01:20-02:45` |
| `/noaudio <url>` | Video without audio | `/noaudio <url>` |
| `/shorts <url>` | Download YouTube Shorts | `/shorts <url>` |
| `/live <url>` | Capture livestream | `/live <url>` |

### 📋 Info & Metadata Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/info <url>` | Video information | `/info <url>` |
| `/format <url>` | List all available formats | `/format <url>` |
| `/thumb <url>` | Download thumbnail | `/thumb <url>` |
| `/metadata <url>` | Export metadata as JSON | `/metadata <url>` |
| `/description <url>` | Get video description | `/description <url>` |
| `/comments <url> [n]` | Get top N comments | `/comments <url> 20` |
| `/chapters <url>` | List video chapters | `/chapters <url>` |
| `/age <url>` | Check age restriction | `/age <url>` |

### 📝 Subtitle Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/subs <url> [lang]` | Download subtitles | `/subs <url> en` |
| `/subslist <url>` | List available languages | `/subslist <url>` |
| `/subslang <code>` | Set default subtitle language | `/subslang hi` |

### 📁 Playlist & Batch Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/pl <url>` | Download playlist | `/pl https://youtube.com/playlist?list=xyz` |
| `/plinfo <url>` | Playlist information | `/plinfo <url>` |
| `/plrange <url> <range>` | Download specific range | `/plrange <url> 1-10` |
| `/batch <urls>` | Download multiple URLs | `/batch url1 url2 url3` |

### 🔍 Search & Discovery

| Command | Description | Example |
|---------|-------------|---------|
| `/search <query>` | Search YouTube | `/search lofi hip hop` |
| `/trending [region]` | Trending videos | `/trending US` |

### ⚙️ Settings Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/settings` | Open settings menu | `/settings` |
| `/setquality <res>` | Set default video quality | `/setquality 720` |
| `/setformat <fmt>` | Set default format | `/setformat mp3` |
| `/setlang <code>` | Set interface language | `/setlang hi` |
| `/setthumb on/off` | Toggle auto-thumbnail | `/setthumb on` |
| `/setsubs on/off` | Toggle auto-subtitles | `/setsubs on` |
| `/setnotify on/off` | Toggle notifications | `/setnotify off` |
| `/setfilename <tpl>` | Set filename template | `/setfilename {uploader} - {title}.{ext}` |
| `/mydefaults` | View current settings | `/mydefaults` |
| `/reset` | Reset all settings | `/reset` |

### 📊 Queue Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/queue` | View download queue | `/queue` |
| `/cancel [id]` | Cancel task | `/cancel 3` |
| `/clearqueue` | Clear entire queue | `/clearqueue` |

### 👥 Group Chat Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/gsettings` | Group settings menu | `/gsettings` |
| `/gallow` | Enable bot in group | `/gallow` |
| `/gdeny` | Disable bot in group | `/gdeny` |
| `/glimit <n>` | Set per-user limit | `/glimit 10` |

### 🔧 Admin Commands (Owner Only)

| Command | Description | Example |
|---------|-------------|---------|
| `/admin` | Admin dashboard | `/admin` |
| `/stats` | Detailed statistics | `/stats` |
| `/broadcast <msg>` | Message all users | `/broadcast Maintenance at 2AM` |
| `/ban <user>` | Ban a user | `/ban @username` |
| `/unban <user>` | Unban a user | `/unban @username` |
| `/setlimit <n>` | Set daily download limit | `/setlimit 50` |
| `/maintenance on/off` | Toggle maintenance mode | `/maintenance on` |
| `/logs` | View recent error logs | `/logs` |
| `/update` | Update yt-dlp | `/update` |
| `/restart` | Restart the bot | `/restart` |

### 💬 Support Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/report <msg>` | Report a bug | `/report Download fails for TikTok` |
| `/feedback <msg>` | Send feedback | `/feedback Great bot!` |
| `/suggest <msg>` | Suggest a feature | `/suggest Add Spotify support` |
| `/speed` | Test download speed | `/speed` |
| `/sponsorblock` | SponsorBlock info | `/sponsorblock` |

> **Total: 70+ commands!**

---

## 📸 Screenshots & Usage

### Flow 1: Simple Audio Download

```
You:  https://youtube.com/watch?v=dQw4w9WgXcQ

Bot:  🎬 Rick Astley - Never Gonna Give You Up (3:33)
      👤 Rick Astley | 👁 1.5B views

      [🎵 Audio]  [🎬 Video]  [📋 Info]
      [📝 Subtitles]  [🖼 Thumbnail]

You:  (clicks 🎵 Audio)

Bot:  🎵 Select Audio Format:
      [MP3 128k]  [MP3 320k]
      [M4A]  [FLAC]  [OGG]  [WAV]

You:  (clicks MP3 320k)

Bot:  ⬇️ Downloading Audio...
      [━━━━━━━━━━━━━━━━━━━━] 100%
      ⚡ Speed: 4.2 MB/s | 📦 8.2 MB

Bot:  🎵 Rick Astley - Never Gonna Give You Up.mp3
      ✅ Download complete!
```

### Flow 2: Video with Quality Selection

```
You:  /mp4 https://youtube.com/watch?v=xyz

Bot:  🎬 Select Video Quality:
      [2160p 4K]  [1440p 2K]  [1080p FHD]
      [720p HD]   [480p]      [360p]
      [Best]      [Smallest]

You:  (clicks 1080p FHD)

Bot:  ⬇️ Downloading Video...
      [━━━━━━━━━━━━░░░░░░░░] 62%
      ⚡ 3.8 MB/s | ⏱ ETA: 0:45 | 📦 156 MB

Bot:  🎬 Video Title [1080p].mp4  ✅
```

### Flow 3: Playlist Download

```
You:  /pl https://youtube.com/playlist?list=PLxyz

Bot:  📁 Playlist: "Python Tutorial Series"
      📹 25 videos | ⏱ 8h 32m total

      [⬇️ All (Audio)]  [⬇️ All (Video)]
      [📊 Select Range]  [📋 List Videos]

You:  (clicks Select Range → 1-10 → MP3 Audio)

Bot:  📥 [1/10] Introduction to Python ✅
      📥 [2/10] Variables & Types ✅
      📥 [3/10] Control Flow ✅
      ...
      🎉 All 10 downloads complete!
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TELEGRAM CLIENT                         │
│                (User sends URL / command)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT API                            │
└────────────────────────┬────────────────────────────────────┘
                         │ Long Polling / Webhook
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  YTGRAB BOT APPLICATION                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Command      │  │  Callback    │  │  URL Auto        │   │
│  │  Handlers     │  │  Handler     │  │  Detector        │   │
│  │  (13 files)   │  │  (inline)    │  │  (regex)         │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                    │              │
│         ▼                 ▼                    ▼              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              MIDDLEWARE LAYER                        │     │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │     │
│  │  │ Rate Limiter │  │ Auth Check   │  │ Logger    │  │     │
│  │  └─────────────┘  └──────────────┘  └───────────┘  │     │
│  └──────────────────────┬──────────────────────────────┘     │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              SERVICE LAYER                           │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │     │
│  │  │ Downloader│ │ Queue    │ │ File     │ │Metadata│ │     │
│  │  │ (yt-dlp) │ │ Manager  │ │ Manager  │ │Service │ │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │     │
│  │  ┌──────────────┐  ┌────────────────────────────┐  │     │
│  │  │ SponsorBlock │  │ FFmpeg (merge/convert/gif) │  │     │
│  │  └──────────────┘  └────────────────────────────┘  │     │
│  └──────────────────────┬──────────────────────────────┘     │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              DATA LAYER                              │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │     │
│  │  │ SQLite   │  │ Temp     │  │ Log Files        │  │     │
│  │  │ (prefs)  │  │ Storage  │  │ (loguru)         │  │     │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11+ | Core application |
| **Bot Framework** | python-telegram-bot v21 | Telegram API interface |
| **Download Engine** | yt-dlp | Media extraction & download |
| **Media Processing** | FFmpeg | Merge, convert, split, GIF |
| **Database** | SQLite (aiosqlite) | User preferences & history |
| **HTTP Client** | aiohttp | Async API calls |
| **Image Processing** | Pillow | Thumbnail handling |
| **Metadata** | mutagen | ID3 tag embedding |
| **Logging** | loguru | Structured logging |
| **Scheduling** | APScheduler | Periodic cleanup tasks |
| **Config** | python-dotenv | Environment variables |
| **Containerization** | Docker | Deployment |

---

## 📁 Project Structure

```
ytgrab-bot/
│
├── bot.py                          # 🚀 Main entry point
├── config.py                       # ⚙️ Configuration & env loading
├── requirements.txt                # 📦 Python dependencies
├── .env                            # 🔑 Environment variables (NOT committed)
├── .env.example                    # 📋 Environment template
├── .gitignore                      # 🚫 Git ignore rules
├── Dockerfile                      # 🐳 Docker image definition
├── docker-compose.yml              # 🐳 Docker compose config
├── Makefile                        # 🔨 Build & run commands
├── README.md                       # 📖 This file
│
├── handlers/                       # 📥 Command & callback handlers
│   ├── __init__.py
│   ├── start_handler.py            #   /start, /help, /faq, callbacks
│   ├── download_handler.py         #   URL detection, /mp3, /mp4, /best
│   ├── playlist_handler.py         #   /pl, /plinfo, /plrange
│   ├── audio_handler.py            #   /m4a, /flac, /ogg, /wav, /opus
│   ├── video_handler.py            #   /webm, /mkv, /gif, /clip, /noaudio
│   ├── admin_handler.py            #   /admin, /stats, /broadcast, /ban
│   ├── settings_handler.py         #   /setquality, /setformat, /reset
│   ├── utility_handler.py          #   /queue, /trending, /batch, /report
│   ├── group_handler.py            #   /gsettings, /gallow, /gdeny
│   ├── subtitle_handler.py         #   /subs, /subslist, /subslang
│   ├── metadata_handler.py         #   /thumb, /metadata, /comments
│   ├── format_handler.py           #   /format, /age, /speed
│   └── advanced_handler.py         #   /audiobook, /live, /chapters
│
├── services/                       # 🔧 Business logic & engines
│   ├── __init__.py
│   ├── downloader.py               #   yt-dlp wrapper + progress hooks
│   ├── queue_manager.py            #   Download queue system
│   ├── file_manager.py             #   File ops, cleanup, split, ZIP, GIF
│   ├── metadata_service.py         #   Full metadata extraction
│   └── sponsorblock_service.py     #   SponsorBlock API integration
│
├── models/                         # 💾 Data models & database
│   ├── __init__.py
│   └── database.py                 #   SQLite async database manager
│
├── utils/                          # 🛠️ Utilities & helpers
│   ├── __init__.py
│   ├── keyboards.py                #   Inline keyboard builders
│   ├── validators.py               #   URL & input validation
│   ├── helpers.py                  #   Formatting, cleanup, disk utils
│   └── constants.py                #   Bot constants & enums
│
├── middleware/                      # 🛡️ Request middleware
│   ├── __init__.py
│   └── rate_limiter.py             #   Sliding window rate limiter
│
├── templates/                      # 💬 Message templates
│   ├── __init__.py
│   ├── messages.py                 #   All bot messages (English)
│   └── i18n.py                     #   Multi-language strings (7 langs)
│
├── deploy/                         # 🚀 Deployment configs
│   ├── ytgrab.service              #   Systemd service file
│   ├── setup.sh                    #   Automated setup script
│   └── nginx.conf                  #   Nginx config (local API)
│
├── tests/                          # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py                 #   Pytest fixtures
│   ├── test_validators.py          #   URL validation tests
│   ├── test_helpers.py             #   Helper function tests
│   ├── test_downloader.py          #   Downloader tests
│   └── test_handlers.py            #   Handler tests
│
├── logs/                           # 📋 Application logs
│   └── bot.log
│
└── data/                           # 💾 SQLite database
    └── ytgrab.db
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# ═══ Required ═══
BOT_TOKEN=your_token_from_botfather    # Telegram Bot API token
ADMIN_ID=123456789                      # Your Telegram user ID

# ═══ Bot Info ═══
BOT_USERNAME=YTGrabDownBot
BOT_NAME=YTGrab Bot

# ═══ Download Settings ═══
MAX_FILE_SIZE_MB=2000                   # Max file size (MB)
MAX_DOWNLOAD_DURATION_MIN=180           # Max video duration (minutes)
MAX_PLAYLIST_ITEMS=100                  # Max playlist videos
MAX_QUEUE_SIZE=10                       # Max queue per user
MAX_CONCURRENT_DOWNLOADS=3              # Simultaneous downloads
TEMP_DIR=/tmp/ytgrab                    # Temp file directory
CLEANUP_INTERVAL_MIN=30                 # Auto-cleanup interval

# ═══ Rate Limiting ═══
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=50
RATE_LIMIT_PER_DAY=100

# ═══ Database ═══
DB_PATH=./data/ytgrab.db

# ═══ Logging ═══
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log

# ═══ Large Files (Optional) ═══
USE_LOCAL_API=false                     # For files > 50MB
LOCAL_API_URL=http://localhost:8081
```

### Filename Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{title}` | Video title | `Never Gonna Give You Up` |
| `{ext}` | File extension | `mp3` |
| `{uploader}` | Channel name | `Rick Astley` |
| `{duration}` | Duration | `3:33` |
| `{upload_date}` | Upload date | `20091025` |
| `{id}` | Video ID | `dQw4w9WgXcQ` |
| `{resolution}` | Video resolution | `1080p` |

**Example:** `/setfilename {uploader} - {title} [{resolution}].{ext}`
→ `Rick Astley - Never Gonna Give You Up [1080p].mp4`

---

## 🚀 Deployment

### Option 1: Oracle Cloud Free Tier (Recommended) 🏆

> **4 CPU cores, 24GB RAM, 200GB storage — FREE forever!**

```bash
# 1. Create account at https://cloud.oracle.com
# 2. Create VM: Ubuntu 22.04, ARM A1 Flex (4 CPU, 24GB)
# 3. SSH into server:
ssh -i your-key.key ubuntu@YOUR_IP

# 4. Install dependencies:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg git

# 5. Setup bot:
git clone https://github.com/YOUR_USERNAME/ytgrab-bot.git
cd ytgrab-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env

# 6. Create systemd service:
sudo cp deploy/ytgrab.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ytgrab

# 7. Verify:
sudo systemctl status ytgrab
# → Active: active (running) ✅
```

### Option 2: Render (Easiest)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Background Worker
3. Connect repo → Set build/start commands → Add env vars → Deploy!

### Option 3: Railway

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add environment variables → Deploy!

### Option 4: Your Own PC

```bash
python bot.py
# Bot runs while terminal is open
```

### Automated Setup Script

```bash
chmod +x deploy/setup.sh
./deploy/setup.sh
# Follow the prompts!
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build & run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Manual Docker

```bash
# Build image
docker build -t ytgrab-bot .

# Run container
docker run -d \
  --name ytgrab \
  --env-file .env \
  -v ytgrab-data:/app/data \
  -v ytgrab-logs:/app/logs \
  --restart unless-stopped \
  --memory 1g \
  ytgrab-bot
```

### Docker Compose Services

| Service | Image | Ports | Volumes |
|---------|-------|-------|---------|
| `ytgrab-bot` | Custom build | None (polling) | data, logs, temp |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_validators.py -v

# Run with coverage report
python -m pytest tests/ -v --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Run only matching tests
python -m pytest tests/ -v -k "test_format"
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `utils/validators.py` | 25+ tests | URL validation, safety, parsing |
| `utils/helpers.py` | 20+ tests | Formatting, truncation, progress |
| `services/downloader.py` | 10+ tests | Duration, speed, format parsing |
| `handlers/` | 10+ tests | URL extraction, command parsing |

---

## 🌐 Multi-Language Support

| Code | Language | Status |
|------|----------|--------|
| `en` | 🇬🇧 English | ✅ Complete |
| `hi` | 🇮🇳 Hindi | ✅ Complete |
| `es` | 🇪🇸 Spanish | ✅ Complete |
| `ar` | 🇸🇦 Arabic | ✅ Complete |
| `fr` | 🇫🇷 French | ✅ Complete |
| `pt` | 🇧🇷 Portuguese | ✅ Complete |
| `ru` | 🇷🇺 Russian | ✅ Complete |
| `ja` | 🇯🇵 Japanese | 🔲 Planned |
| `ko` | 🇰🇷 Korean | 🔲 Planned |
| `zh` | 🇨🇳 Chinese | 🔲 Planned |

**Change language:** `/setlang hi`

---

## 🔒 Rate Limiting & Security

### Rate Limits

| Scope | Limit | Window |
|-------|-------|--------|
| Per user | 10 downloads | Per minute |
| Per user | 50 downloads | Per hour |
| Per user | 100 downloads | Per day |
| Per group | 30 downloads | Per hour |
| Global | 500 downloads | Per hour |
| File size | 2 GB | Per file |
| Video duration | 3 hours | Per video |
| Playlist | 100 items | Per playlist |

### Security Measures

- ✅ URL validation (blocks malicious/internal URLs)
- ✅ Input sanitization (prevents command injection)
- ✅ File type validation (blocks .exe, .sh, .bat, etc.)
- ✅ Sliding window rate limiter
- ✅ Auto-ban after repeated violations
- ✅ Environment variables for secrets (never hardcoded)
- ✅ Non-root Docker user
- ✅ Systemd security hardening

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `BOT_TOKEN is not set` | Edit `.env` → Add your token |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `ffmpeg not found` | `sudo apt install ffmpeg` |
| Bot not responding | `sudo systemctl status ytgrab` → Check logs |
| Download fails | `pip install -U yt-dlp` → Restart bot |
| File too large (>50MB) | Set `USE_LOCAL_API=true` in `.env` |
| `Permission denied` | `chmod 600 .env` / `chmod 400 key.pem` |
| High memory usage | Reduce `MAX_CONCURRENT_DOWNLOADS` |
| yt-dlp extractor error | `pip install -U yt-dlp` (YouTube changes often) |
| Bot crashes on restart | Check `sudo journalctl -u ytgrab -n 50` |

### Useful Debug Commands

```bash
# Live logs
sudo journalctl -u ytgrab -f

# Last 50 log lines
sudo journalctl -u ytgrab -n 50

# Check service status
sudo systemctl status ytgrab

# Restart bot
sudo systemctl restart ytgrab

# Check disk space
df -h /tmp

# Check temp files
du -sh /tmp/ytgrab/

# Update yt-dlp manually
cd ~/ytgrab-bot && source venv/bin/activate
pip install -U yt-dlp
sudo systemctl restart ytgrab
```

---

## 🗺️ Roadmap

### ✅ v1.0 (Current)
- [x] Core audio/video download (7 audio + 4 video formats)
- [x] 1000+ platform support via yt-dlp
- [x] Inline keyboard interface
- [x] Playlist download (up to 100 videos)
- [x] Subtitle & thumbnail download
- [x] YouTube search & trending
- [x] User settings & preferences
- [x] Group chat support
- [x] Admin dashboard
- [x] Queue management
- [x] Multi-language (7 languages)
- [x] Rate limiting & security
- [x] GIF conversion & time-range clipping
- [x] Audiobook chapter splitting
- [x] SponsorBlock integration
- [x] Docker & systemd deployment

### 🔲 v1.1 (Next)
- [ ] Spotify track download (via YouTube search)
- [ ] Telegram channel media downloader
- [ ] Audio cutter/trimmer
- [ ] Video compression options
- [ ] 3 more languages (Japanese, Korean, Chinese)

### 🔲 v1.2 (Future)
- [ ] Telegram Mini App (Web App) interface
- [ ] Cloud storage upload (Google Drive, Mega)
- [ ] Scheduled downloads
- [ ] Web dashboard (FastAPI)

### 🔲 v2.0 (Vision)
- [ ] AI-powered video summarization
- [ ] Voice command support
- [ ] Multi-bot instance (load balancing)
- [ ] Plugin system for custom extractors

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing`
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/ytgrab-bot.git
cd ytgrab-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov flake8   # Dev dependencies
cp .env.example .env                   # Configure
python -m pytest tests/ -v             # Run tests
```

### Code Style

- Follow PEP 8
- Max line length: 120
- Use type hints
- Add docstrings to all functions
- Write tests for new features

---

## ⚖️ Legal Disclaimer

> ⚠️ **IMPORTANT:** This bot is intended for **personal and educational use only**.
>
> - Users are **solely responsible** for complying with copyright laws in their jurisdiction.
> - The bot **does not host, store, or redistribute** any content.
> - All downloads are processed **on-the-fly** and temp files are **auto-deleted**.
> - The bot **does NOT bypass** DRM, paywalls, or age restrictions.
> - Downloading copyrighted content for redistribution may be **illegal** in your country.
>
> **Use at your own risk. The developers are not responsible for misuse.**

---

## 🙏 Credits

| Project | Role | Link |
|---------|------|------|
| **yt-dlp** | Download engine (1000+ extractors) | [GitHub](https://github.com/yt-dlp/yt-dlp) |
| **python-telegram-bot** | Telegram Bot API framework | [GitHub](https://github.com/python-telegram-bot/python-telegram-bot) |
| **FFmpeg** | Media processing & conversion | [ffmpeg.org](https://ffmpeg.org) |
| **SponsorBlock** | Sponsor segment database | [sponsor.ajay.app](https://sponsor.ajay.app) |
| **loguru** | Structured logging | [GitHub](https://github.com/Delgan/loguru) |
| **aiosqlite** | Async SQLite database | [GitHub](https://github.com/omnilib/aiosqlite) |
| **mutagen** | Audio metadata embedding | [GitHub](https://github.com/quodlibet/mutagen) |
| **Pillow** | Image processing | [GitHub](https://github.com/python-pillow/Pillow) |

---

## 📞 Support

| Channel | Link |
|---------|------|
| 🤖 **Bot** | [@YTGrabDownBot](https://t.me/YTGrabDownBot) |
| 🐛 **Bug Report** | Use `/report` in bot or [GitHub Issues](https://github.com/YOUR_USERNAME/ytgrab-bot/issues) |
| 💬 **Feedback** | Use `/feedback` in bot |
| 💡 **Feature Request** | Use `/suggest` in bot |
| 📖 **Documentation** | This README + `/help` in bot |

---

## 📄 License

This project is **free and open source**. Use at your own risk.

```
No warranty. No liability. Personal/educational use only.
```

---

<div align="center">

**Made with ❤️ by developers, for everyone.**

**100% Free. No Ads. No Registration. Forever.**

[⬆️ Back to Top](#-ytgrab-bot)

</div>

**That's the complete README, bro! Looks professional on GitHub! 🚀🔥**
