# Installation Guide

This guide covers how to install IotaPlayer on different operating systems.

## Windows Installation

### Option 1: Pre-built Executable (Recommended)

1. **Download the latest release** from the [Releases Page](https://github.com/vorlie/IotaPlayer/releases)
2. **Extract the ZIP file** to your desired location
3. **Run `IotaPlayer.exe`** to start the application

### Option 2: From Source

1. **Install Python 3.13+** from [python.org](https://python.org)
2. **Clone the repository:**
   ```cmd
   git clone https://github.com/vorlie/IotaPlayer.git
   cd IotaPlayer
   ```
3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt --ignore-requires-python
   ```
4. **Run the application:**
   ```cmd
   python main.py
   ```

## Linux Installation

### Option 1: One-Command Installer (Recommended)

The installer script provides the easiest way to install IotaPlayer on Linux:

1. **Download the installer:**
   ```bash
   curl -O https://raw.githubusercontent.com/vorlie/IotaPlayer/main/linux_installer.sh
   ```

2. **Make it executable:**
   ```bash
   chmod +x linux_installer.sh
   ```

3. **Run the installer:**
   ```bash
   # For fresh installation
   ./linux_installer.sh install
   
   # For updates
   ./linux_installer.sh update
   ```

The script will:
- Detect your Linux distribution
- Install system dependencies (GStreamer, Qt6)
- Set up Python virtual environment
- Build the application with PyInstaller
- Create desktop shortcuts (optional)

### Option 2: Manual Installation

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
  libxcb-xinerama0 python3-venv python3-pip
```

**Arch Linux:**
```bash
sudo pacman -Syu gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad \
  gst-plugins-ugly gst-libav qt6-multimedia python python-pip
```

#### Step 2: Clone and Setup

```bash
git clone https://github.com/vorlie/IotaPlayer.git
cd IotaPlayer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Run the Application

```bash
python main.py
```

## System Dependencies

### Windows
- **Python 3.13+** (for source installation)
- **DirectShow codecs** (usually included with Windows)
- **K-Lite Codec Pack** (recommended for better codec support)

### Linux
- **Python 3.13+**
- **GStreamer plugins** (for audio playback)
- **PyQt6** (for the GUI)
- **Additional libraries** (see troubleshooting for specific distros)

## Post-Installation

### First Launch
1. **Launch IotaPlayer** from your installation
2. **Configure settings** in the Settings dialog
3. **Set up Discord integration** (optional)
4. **Configure Google API** for YouTube features (optional)

### Configuration Files
IotaPlayer stores configuration in:
- **Linux/macOS:** `~/.config/IotaPlayer/config.json`
- **Windows:** `%APPDATA%\IotaPlayer\config.json`

## Troubleshooting

### Common Issues

**"No module named 'PyQt6'"**
```bash
pip install PyQt6 PyQt6-Qt6 PyQt6-sip
```

**Audio not playing (Linux)**
```bash
# Install additional GStreamer plugins
sudo apt install gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

**Qt platform errors (Linux)**
```bash
# Install additional Qt libraries
sudo apt install libxcb-xinerama0 libxcb1 libx11-xcb1 libgl1-mesa-glx
```

**Wayland issues (Linux)**
```bash
# Force XCB platform
export QT_QPA_PLATFORM=xcb
python main.py
```

### Getting Help

- Check the [Troubleshooting](Troubleshooting) page for more solutions
- Visit [GitHub Issues](https://github.com/vorlie/IotaPlayer/issues) to report problems
- Review the [Configuration](Configuration) guide for advanced setup

## Building from Source

### Prerequisites
- Python 3.13+
- PyInstaller 6.6.0+
- All system dependencies

### Build Commands

**Windows:**
```cmd
pip install pyinstaller==6.6.0
pyinstaller IotaPlayerWIN.spec
```

**Linux:**
```bash
pip install pyinstaller==6.6.0
pyinstaller IotaPlayerLinux.spec
```

The built executable will be in the `dist/` directory.

---

**Next Steps:**
- [User Guide](User-Guide) - Learn how to use IotaPlayer
- [Configuration](Configuration) - Customize your setup
- [Troubleshooting](Troubleshooting) - Solve common issues 