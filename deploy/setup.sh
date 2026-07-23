#!/bin/bash
# ═══════════════════════════════════════════════════════════
# YTGrab Bot - Automated Setup Script
# Bot: @YTGrabDownBot
# Usage: chmod +x deploy/setup.sh && ./deploy/setup.sh
# ═══════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════════════"
echo "  🚀 YTGrab Bot Setup"
echo "  📱 @YTGrabDownBot"
echo "═══════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root for system packages
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  System packages need sudo. Continuing with user setup...${NC}"
fi

# 1. Install system dependencies
echo -e "\n${GREEN}📦 Installing system dependencies...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3.11 python3.11-venv python3-pip ffmpeg git curl
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 ffmpeg git curl
elif command -v brew &> /dev/null; then
    brew install python@3.11 ffmpeg
fi

# 2. Create virtual environment
echo -e "\n${GREEN}🐍 Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
echo -e "\n${GREEN}📚 Installing Python packages...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 4. Create directories
echo -e "\n${GREEN}📁 Creating directories...${NC}"
mkdir -p logs data /tmp/ytgrab/downloads /tmp/ytgrab/processing

# 5. Create .env if not exists
if [ ! -f .env ]; then
    echo -e "\n${GREEN}📝 Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Edit .env with your bot token!${NC}"
    echo -e "   nano .env"
else
    echo -e "\n${GREEN}✅ .env already exists${NC}"
fi

# 6. Setup systemd service (optional)
echo -e "\n${YELLOW}🔧 Setup systemd service? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo cp deploy/ytgrab.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable ytgrab
    echo -e "${GREEN}✅ Service installed! Start with: sudo systemctl start ytgrab${NC}"
fi

# 7. Verify installation
echo -e "\n${GREEN}🔍 Verifying installation...${NC}"
python3 -c "import telegram; print(f'  ✅ python-telegram-bot: {telegram.__version__}')"
python3 -c "import yt_dlp; print(f'  ✅ yt-dlp: {yt_dlp.version.__version__}')"
ffmpeg -version 2>/dev/null | head -1 | sed 's/^/  ✅ /'

echo ""
echo "═══════════════════════════════════════════════"
echo -e "  ${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "  Next steps:"
echo "  1. Edit .env:     nano .env"
echo "  2. Run bot:       python bot.py"
echo "  3. Or service:    sudo systemctl start ytgrab"
echo ""
echo "  📱 Bot: @YTGrabDownBot"
echo "═══════════════════════════════════════════════"
