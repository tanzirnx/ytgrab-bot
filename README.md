# 🎬 YTGrab Bot

> **Free YouTube & Media Downloader Telegram Bot**
> Download audio, video, playlists, subtitles & thumbnails from 1000+ websites.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-green.svg)](https://github.com/yt-dlp/yt-dlp)
[![License](https://img.shields.io/badge/License-Free-brightgreen.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-@YTGrabDownBot-2CA5E0.svg)](https://t.me/YTGrabDownBot)

---

## ✨ Features

### 🎵 Audio Download
- MP3, M4A, FLAC, OGG, WAV, OPUS, AAC
- Bitrate: 64kbps to 320kbps
- Auto-embed thumbnail as album art
- Auto-embed metadata (ID3 tags)

### 🎬 Video Download
- MP4, WEBM, MKV
- Quality: 144p to 4K (2160p)
- Auto-merge best video + audio
- GIF conversion
- Time-range clipping
- Video without audio

### 📁 Playlist Support
- Download up to 100 videos
- Select range (1-10, 11-20, etc.)
- Choose format for all
- Progress tracking

### 📝 Subtitles
- Download in any language
- SRT, VTT, ASS, JSON3 formats
- Auto-generated subtitles
- List available languages

### 🖼 Thumbnails
- Best quality thumbnails
- JPG, PNG, WEBP formats

### 🔍 Search
- Search YouTube from bot
- Trending videos by region
- Inline result selection

### ⚙️ Settings
- Default format & quality
- Auto-thumbnail toggle
- Auto-subtitle toggle
- Custom filename template
- Multi-language (7 languages)

### 👥 Group Chat
- Works in groups
- Admin controls
- Per-user limits
- Silent mode

### 🛡️ Security & Privacy
- No data logging
- No user tracking
- Rate limiting
- Input sanitization
- GDPR compliant

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- FFmpeg
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ytgrab-bot.git
cd ytgrab-bot

# Automated setup
chmod +x deploy/setup.sh
./deploy/setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install ffmpeg  # Install FFmpeg

# Configure
cp .env.example .env
nano .env  # Add your BOT_TOKEN and ADMIN_ID

# Run
python bot.py
