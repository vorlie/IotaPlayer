# IotaPlayer

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

A feature-rich desktop music player for Windows and Linux with Discord Rich Presence, YouTube integration, and powerful playlist management.

## 🎵 Features

- **🎵 Playlist Management** - Create, edit, and manage playlists with ease
- **🎮 Playback Controls** - Full media controls with keyboard shortcuts
- **🎨 Modern UI** - Dark/light themes with customizable accent colors
- **🔗 Discord Integration** - Rich Presence showing current song
- **📺 YouTube Integration** - Upload playlists and open videos
- **🖼️ Cover Art** - Automatic extraction and caching
- **🔄 Auto Updates** - In-app update system
- **🎹 Media Keys** - Full keyboard media key support

## 🚀 Quick Start

### Windows
1. Download from [Releases](https://github.com/vorlie/IotaPlayer/releases)
2. Extract and run `IotaPlayer.exe`

### Linux
```bash
# One-command installer
curl -O https://raw.githubusercontent.com/vorlie/IotaPlayer/main/linux_installer.sh
chmod +x linux_installer.sh
./linux_installer.sh install
```

### From Source
```bash
git clone https://github.com/vorlie/IotaPlayer.git
cd IotaPlayer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --ignore-requires-python
python main.py
```

## 📖 Documentation

**📚 [Full Documentation Wiki](https://github.com/vorlie/IotaPlayer/wiki)**

- **[Installation Guide](https://github.com/vorlie/IotaPlayer/wiki/Installation)** - Detailed setup instructions
- **[User Guide](https://github.com/vorlie/IotaPlayer/wiki/User-Guide)** - Complete feature walkthrough
- **[Configuration](https://github.com/vorlie/IotaPlayer/wiki/Configuration)** - Settings and customization
- **[Troubleshooting](https://github.com/vorlie/IotaPlayer/wiki/Troubleshooting)** - Common issues and solutions
- **[Contributing](https://github.com/vorlie/IotaPlayer/wiki/Contributing)** - Development guidelines

## 🖼️ Screenshots

<details>
<summary>View Screenshots</summary>

| Main Window | Playlist Maker | Settings |
|:---:|:---:|:---:|
| ![Main Interface](images/IotaPlayer_MainWindowDark.png) | ![Playlist Maker](images/IotaPlayer_PlaylistMakerDark.png) | ![Settings](images/IotaPlayer_SettingsDark.png) |

</details>

## 🎯 Key Features

### Playlist Management
- Create and edit playlists with the built-in Playlist Maker
- Load, reload, and combine playlists
- Support for various audio formats (MP3, FLAC, OGG, WAV, M4A)

### Playback & Audio
- Standard controls: play, pause, stop, next, previous
- Loop and shuffle modes
- Seek bar for precise navigation
- Volume control with slider
- Media key support

### Integrations
- **Discord Rich Presence** - Show current song in Discord status
- **YouTube Integration** - Upload playlists and open videos
- **MPRIS Support (Linux)** - Desktop environment integration

### User Interface
- Song information display (artist, title, album, genre)
- Dynamic window title updates
- Customizable accent colors
- Cover art extraction and caching
- Modern settings dialog with organized tabs

## 🔧 System Requirements

- **Python 3.13+** (for source installation)
- **Windows 10/11** or **Linux** (Ubuntu, Debian, Arch, etc.)
- **GStreamer** (Linux) or **K-Lite** (Windows) for audio playback
- **PyQt6** for the user interface

## 🛠️ Development

### Prerequisites
- Python 3.13+
- Git
- PyQt6 and dependencies

### Setup
```bash
git clone https://github.com/vorlie/IotaPlayer.git
cd IotaPlayer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --ignore-requires-python
python main.py
```

### Building
```bash
# Windows
pyinstaller IotaPlayerWIN.spec

# Linux
pyinstaller IotaPlayerLinux.spec
```

## 🤝 Contributing

We welcome contributions! Please see our **[Contributing Guide](https://github.com/vorlie/IotaPlayer/wiki/Contributing)** for details.

- 🐛 **Report bugs** on [GitHub Issues](https://github.com/vorlie/IotaPlayer/issues)
- 💡 **Request features** via GitHub Issues
- 📝 **Improve documentation** in the wiki
- 🔧 **Submit pull requests** for code improvements

## 📋 To-Do List

[**View our To-Do List on GitHub Projects**](https://github.com/users/vorlie/projects/3/views/1)

## 🙏 Acknowledgments

### Special Thanks
- **[DarkDetect](https://github.com/albertosottile/darkdetect)** - Windows dark mode detection
- **[qdarktheme](https://github.com/vorlie/PyQtDarkTheme)** - Dark theme integration

### Dependencies
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/intro)** - GUI framework
- **[pypresence](https://pypi.org/project/pypresence/)** - Discord Rich Presence
- **[mutagen](https://mutagen.readthedocs.io/)** - Audio metadata handling
- **[pynput](https://pynput.readthedocs.io/)** - Media key support
- **[pyinstaller](https://www.pyinstaller.org/)** - Application packaging

## 📄 License

This project is licensed under the **GNU General Public License v3**. See the [LICENSE](LICENSE) file for details.

---

**⭐ Star this repository if you find it useful!**

**📚 [View Full Documentation](https://github.com/vorlie/IotaPlayer/wiki)**