#!/usr/bin/env bash
set -e

echo "IotaPlayer Linux Installer"
echo "-------------------------"

if [ ! -f main.py ]; then
    echo "Project files not found in current directory."
    read -p "Clone the IotaPlayer repository here? (y/n): " clone_repo
    if [[ "$clone_repo" =~ ^[Yy]$ ]]; then
        git clone https://github.com/vorlie/IotaPlayer.git
        cd IotaPlayer
    else
        echo "Please run this installer from the IotaPlayer project directory."
        exit 1
    fi
fi

# 1. Detect distro and install system dependencies
if [ -f /etc/arch-release ]; then
    echo "Detected Arch Linux."
    sudo pacman -Syu --needed gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav \
        qt5-multimedia
elif [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu."
    sudo apt update
    sudo apt install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
        libxcb-xinerama0
else
    echo "Unknown distro. Please install Python 3.12+, PyQt5, and GStreamer plugins manually."
fi

# 2. Set up venv and install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --ignore-requires-python

# 3. Build the executable
if [ -f IotaPlayerLinux.spec ]; then
    pyinstaller IotaPlayerLinux.spec
else
    echo "PyInstaller spec file not found!"
    exit 1
fi

# 4. Ask user for install path
read -e -p "Enter installation directory (default: $HOME/Apps/IotaPlayer): " install_path
install_path=${install_path:-$HOME/Apps/IotaPlayer}
mkdir -p "$install_path"

# 5. Copy built files
cp -r dist/IotaPlayer/* "$install_path/"
if [ -f icon.png ]; then
    cp icon.png "$install_path/icon.png"
fi

# 6. Generate run.sh
cat > "$install_path/run_iotaplayer.sh" <<EOF
#!/usr/bin/env bash
export GST_PLUGIN_SCANNER=/usr/lib/gstreamer-1.0/gst-plugin-scanner
export GST_PLUGIN_PATH=/usr/lib/gstreamer-1.0
export GST_PLUGIN_SYSTEM_PATH=/usr/lib/gstreamer-1.0
exec "$install_path/IotaPlayer"
EOF
chmod +x "$install_path/run_iotaplayer.sh"

echo "run_iotaplayer.sh created at $install_path."

# 7. (Optional) Generate .desktop file
read -p "Create desktop shortcut? (y/n): " create_shortcut
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
    echo "Shortcut created. You may need to log out and back in for it to appear."
fi

echo "Installation complete! Launch with: $install_path/run_iotaplayer.sh"
