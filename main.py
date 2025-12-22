# IotaPlayer - A feature-rich music player application
# Copyright (C) 2025 Charlie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# ./main.py
# =============
# This is the main entry point for IotaPlayer, initializing the application,
# setting up the GUI, and managing the main event loop.
# It handles configuration loading, theme management, and server setup for single instance enforcement.
# =============
import sys
import json
import platform
import logging
import darkdetect
import os
import utils
import qdarktheme # noqa: F401
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QObject, pyqtSlot, QT_VERSION_STR
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from core.configManager import ConfigManager
from config import ICON_PATH, default_settings, get_system_qt_version, is_version_higher
from core.mprisThread import start_mpris

setup_logging()

# Configuration now managed by ConfigManager singleton
config_manager = ConfigManager.get_instance()
CONFIG_PATH = config_manager.get_config_path()
DEFAULT_ACCENT_COLOR = "#ff50aa"
DEFAULT_BACKGROUND_COLOR = "#4d1833"

class Application:
    """Main application class managing lifecycle and player instance."""
    
    def __init__(self):
        self.player = None
        self.iota_server = None
        self.lock_file = None
        self.lock_fd = None


class Iota(QObject):
    def __init__(self, player_instance):
        super().__init__()
        self.server = None
        self.player = player_instance  # Store player reference instead of using global

    def setup_server(self):
        self.server = QLocalServer(self)
        if self.server.listen("IotaPlayerInstance"):
            logging.info("Server started, listening for incoming connections.")
        else:
            logging.error(f"Server failed to start: {self.server.errorString()}")
        self.server.newConnection.connect(self.handle_new_connection)

    @pyqtSlot()  # Explicitly mark as a slot
    def handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(1000)
            message = socket.readAll().data().decode()
            if message == "focus":
                self.bring_to_foreground()

    def bring_to_foreground(self):
        logging.info(f"Attempting to bring window to foreground on {platform.system()}.")
        if platform.system() == "Windows":
            import ctypes
            from ctypes.wintypes import HWND
            hwnd = int(self.player.winId())
            logging.info(f"Windows HWND: {hwnd}")
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(HWND(hwnd), SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(HWND(hwnd))
            ctypes.windll.user32.SetFocus(HWND(hwnd))
        else:
            self.player.raise_()
            self.player.activateWindow()

def check_qt_compatibility(config):
    """Check Qt version compatibility and show warning if needed."""
    system_qt = get_system_qt_version()
    if system_qt and is_version_higher(system_qt, QT_VERSION_STR):
        if not config.get("use_qdarktheme", False):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Qt Version Mismatch")
            msg.setText(f"System Qt version ({system_qt}) is newer than bundled Qt version ({QT_VERSION_STR})")
            msg.setInformativeText(
                "This may cause theme inconsistencies. Would you like to enable QDarkTheme "
                "for a consistent appearance?"
            )
            msg.setDetailedText(
                "Your system's Qt version is newer than the one bundled with PyQt6. "
                "This can cause visual glitches when using system themes like Breeze. "
                "Using QDarkTheme instead will provide a consistent appearance."
            )
            enable_button = msg.addButton("Enable QDarkTheme", QMessageBox.ButtonRole.YesRole)
            msg.addButton("Keep Current Theme", QMessageBox.ButtonRole.NoRole)
            
            msg.exec()
            
            if msg.clickedButton() == enable_button:
                config["use_qdarktheme"] = True
                with open(CONFIG_PATH, 'w') as f:
                    json.dump(config, f, indent=4)
                return True
    return False

def load_config():
    """Load configuration using ConfigManager with fallback to defaults."""
    try:
        return config_manager.load_config()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config: {e}")
        return default_settings

def is_instance_running(server_name="IotaPlayerInstance"):
    """Send focus message to running instance if it exists."""
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    is_running = socket.waitForConnected(1000)
    if is_running:
        logging.info("Sending focus message to the running instance")
        socket.write(b"focus")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
    return is_running

def acquire_instance_lock():
    """Acquire file-based lock to ensure single instance.
    
    Returns:
        tuple: (lock_file_path, lock_fd) if lock acquired, (None, None) if another instance running
    """
    import fcntl
    
    lock_file = os.path.join(config_manager.get_config_dir(), ".iota.lock")
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    try:
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write PID to lock file for debugging
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        logging.info(f"Acquired instance lock: {lock_file}")
        return lock_file, lock_fd
    except (IOError, OSError) as e:
        logging.info(f"Could not acquire lock (another instance running): {e}")
        # Another instance is running, try to send focus message
        is_instance_running()
        return None, None

def release_instance_lock(lock_file, lock_fd):
    """Release the instance lock."""
    if lock_fd:
        import fcntl
        try:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
            if lock_file and os.path.exists(lock_file):
                os.remove(lock_file)
            logging.info("Released instance lock")
        except Exception as e:
            logging.error(f"Error releasing lock: {e}")
        
def main():
    app = QApplication(sys.argv)
    application = Application()
    
    # Acquire instance lock (prevents race condition)
    lock_file, lock_fd = acquire_instance_lock()
    if lock_file is None:
        logging.info("Another instance is already running. Exiting.")
        sys.exit(0)
    
    application.lock_file = lock_file
    application.lock_fd = lock_fd
    
    config = load_config()
    
    needs_restart = check_qt_compatibility(config)
    if needs_restart:
        QMessageBox.information(
            None, 
            "Restart Required",
            "Please restart IotaPlayer for the theme changes to take effect."
        )
        release_instance_lock(lock_file, lock_fd)
        sys.exit(0)
    
    font_name_from_config = config.get("font_name", "Noto Sans")
    font_size = 10
    font_weight = QFont.Weight.Normal
    custom_font_family = font_name_from_config
    global_font = QFont(custom_font_family, font_size, font_weight)
    app.setFont(global_font)
    color = config.get("colorization_color", "automatic")  

    dark_mode = config.get("dark_mode", False)
    if platform.system() == "Linux":
        theme = "dark" if dark_mode else "light"
    else:
        theme = darkdetect.theme().lower()

    if color == "automatic":
        if platform.system() == "Windows":
            clr = utils.get_colorization_colors()[0]
        else:
            clr = "#ff50aa"  # Or any default/accent color for Linux
    else:
        clr = color
    
    # Create player instance (no global variable)
    # Check if icon exists
    if not os.path.exists(ICON_PATH):
        logging.warning(f"Icon file not found at {ICON_PATH}. Application will run without default icon.")

    application.player = MusicPlayer(
        settings=default_settings,
        icon_path=ICON_PATH,
        config_path=CONFIG_PATH,
        theme=theme,
        normal=clr,
        config=config  # Pass loaded config
    )
    
    # Setup Iota server with player reference
    application.iota_server = Iota(application.player)
    application.iota_server.setup_server()
    
    application.player.show()
    application.player.adjust_volume(application.player.get_volume)

    # Start MPRIS integration (Linux only)
    if platform.system() == "Linux":
        start_mpris(application.player)

    if config.get("use_qdarktheme", False):
        qdarktheme.setup_theme("dark" if config.get("dark_mode", False) else "light")

    exit_code = app.exec()
    
    # Cleanup: release lock on exit
    release_instance_lock(lock_file, lock_fd)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
