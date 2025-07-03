#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}IotaPlayer Linux Installer${NC}"
echo -e "${CYAN}-------------------------${NC}"

if [ "$(basename "$PWD")" = "IotaPlayer" ]; then
    :
elif [ -d IotaPlayer ]; then
    cd IotaPlayer
else
    echo -e "${YELLOW}Project directory 'IotaPlayer' not found in current directory.${NC}"
    echo -en "${CYAN}Clone the IotaPlayer repository here? (y/n): ${NC}"
    read clone_repo
    if [[ "$clone_repo" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cloning repository...${NC}"
        git clone https://github.com/vorlie/IotaPlayer.git
        cd IotaPlayer
    else
        echo -e "${RED}Please run this installer from the IotaPlayer project directory.${NC}"
        exit 1
    fi
fi

# 1. Detect distro and install system dependencies
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}Detected Arch Linux.${NC}"
    sudo pacman -S --needed gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav \
        qt5-multimedia
elif [ -f /etc/debian_version ]; then
    echo -e "${GREEN}Detected Debian/Ubuntu.${NC}"
    sudo apt update
    sudo apt install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
        libxcb-xinerama0
else
    echo -e "${RED}Unknown distro. Please install Python 3.13+, PyQt5, and GStreamer plugins manually.${NC}"
fi

# 2. Set up venv and install Python dependencies
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv venv
echo -e "${BLUE}Activating venv and installing requirements...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --ignore-requires-python

echo -e "${BLUE}Building the executable...${NC}"
# 3. Build the executable
if [ -f IotaPlayerLinux.spec ]; then
    pyinstaller IotaPlayerLinux.spec --noconfirm
else
    echo -e "${RED}PyInstaller spec file not found!${NC}"
    exit 1
fi

# 4. Ask user for install path
echo -en "${CYAN}Enter installation directory (default: $HOME/Apps/IotaPlayer): ${NC}"
read -e install_path
install_path=${install_path:-$HOME/Apps/IotaPlayer}
mkdir -p "$install_path"

echo -e "${BLUE}Copying built files...${NC}"
# 5. Copy built files
cp -r dist/IotaPlayer/* "$install_path/"
if [ -f icon.png ]; then
    cp icon.png "$install_path/icon.png"
fi

echo -e "${BLUE}Generating launcher script...${NC}"
# 6. Generate run.sh
cat > "$install_path/run_iotaplayer.sh" <<EOF
#!/usr/bin/env bash
export GST_PLUGIN_SCANNER=/usr/lib/gstreamer-1.0/gst-plugin-scanner
export GST_PLUGIN_PATH=/usr/lib/gstreamer-1.0
export GST_PLUGIN_SYSTEM_PATH=/usr/lib/gstreamer-1.0
exec "$install_path/IotaPlayer"
EOF
chmod +x "$install_path/run_iotaplayer.sh"

echo -e "${GREEN}run_iotaplayer.sh created at $install_path.${NC}"

# 7. (Optional) Generate .desktop file
echo -en "${CYAN}Create desktop shortcut? (y/n): ${NC}"
read create_shortcut
if [[ "$create_shortcut" =~ ^[Yy]$ ]]; then
    cat > "$install_path/IotaPlayer.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=IotaPlayer
Exec=$install_path/run_iotaplayer.sh
Icon=$install_path/icon.png
Comment=Music player
Categories=AudioVideo;Player;
Terminal=false
EOF
    cp "$install_path/IotaPlayer.desktop" ~/.local/share/applications/
    chmod +x ~/.local/share/applications/IotaPlayer.desktop
    echo -e "${GREEN}Shortcut created. You may need to log out and back in for it to appear.${NC}"
fi

echo -e "${GREEN}Installation complete! Launch with: $install_path/run_iotaplayer.sh${NC}"
