# ./main.py
# =============
# This is the main entry point for IotaPlayer, initializing the application,
# setting up the GUI, and managing the main event loop.
# It handles configuration loading, theme management, and server setup for single instance enforcement.
# =============
import qdarktheme as qdt
import sys
import json
import platform
import logging
import darkdetect
import os
from time import sleep
import utils
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from config import ICON_PATH, default_settings
from core.mprisThread import start_mpris

setup_logging()

def get_config_path():
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "IotaPlayer", "config.json")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "IotaPlayer", "config.json")

CONFIG_PATH = get_config_path()
DEFAULT_ACCENT_COLOR = "#ff50aa"
DEFAULT_BACKGROUND_COLOR = "#4d1833"

class ColorChangeListener(QThread):
    color_changed = pyqtSignal(str, str, str, str, str)  # Emit color only
    
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

    def run(self):
        logging.info("ColorChangeListener started.")
        utils.listener(self.on_color_change)

    def on_color_change(self, normal, dark, dark_alt, light, light_alt):
        logging.info(f"Detected color change: {normal}, {dark}, {dark_alt}, {light}, {light_alt}")
        self.color_changed.emit(normal, dark, dark_alt, light, light_alt)

class ThemeChangeListener(QThread):
    theme_changed = pyqtSignal(str)  # Emit theme only
    
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.current_theme = darkdetect.theme().lower()

    def run(self):
        logging.info("ThemeChangeListener started.")
        while True:
            new_theme = darkdetect.theme().lower()
            if new_theme != self.current_theme:
                self.current_theme = new_theme
                self.on_theme_change(new_theme)
            sleep(5)

    def on_theme_change(self, theme):
        logging.info(f"Detected theme change: {theme}")
        self.theme_changed.emit(theme)

class Iota(QObject):
    def __init__(self):
        super().__init__()
        self.server = None

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
            hwnd = int(player.winId())
            logging.info(f"Windows HWND: {hwnd}")
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(HWND(hwnd), SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(HWND(hwnd))
            ctypes.windll.user32.SetFocus(HWND(hwnd))
        else:
            player.raise_()
            player.activateWindow()


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config: {e}")
        return default_settings

def update_theme(normal, dark, dark_alt, light, light_alt, theme):
    logging.info(f"Updating theme to: {theme}")
    if theme == 'dark':
        qdt.setup_theme('dark', 
            custom_colors={
                "primary": normal, 
                "background": dark, 
                #"border": dark_alt,
                "input.background": dark,
                "foreground>input.placeholder": "#bababa",
                "foreground": "#ffffff"})
    else:
        qdt.setup_theme('light', 
            custom_colors={
                "primary": normal, 
                "background": light, 
                #"border": light_alt, 
                "input.background": light,
                "foreground>input.placeholder": "#313131",
                "border":"#3f4042",
                "foreground": "#000000"})

def is_instance_running(server_name="IotaPlayerInstance"):
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    is_running = socket.waitForConnected(1000)
    if is_running:
        logging.info("Sending focus message to the running instance")
        socket.write(b"focus")  # Send a message to the running instance
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
    return is_running
        
def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    
    if is_instance_running():
        logging.info("Another instance of the application is already running.")
        sys.exit(0)  # Exit the current instance
        
    IotaSrv = Iota()

    IotaSrv.setup_server()
    config = load_config()
    font_name_from_config = config.get("font_name", "Noto Sans")
    font_size = 10
    font_weight = QFont.Normal
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
    global player
    player = MusicPlayer(
        settings=default_settings, 
        icon_path=ICON_PATH, 
        config_path=CONFIG_PATH, 
        theme=theme,
        normal=clr
    )
    player.show()
    player.adjust_volume(player.get_volume)

    # Start MPRIS integration (Linux only)
    if platform.system() == "Linux":
        start_mpris(player)

    def handle_color_change(normal, dark, dark_alt, light, light_alt):
        current_theme = darkdetect.theme().lower()
        logging.info(f"Handling color change: {normal}, {dark}, {dark_alt}, {light}, {light_alt} for theme: {current_theme}")
        normal, dark, dark_alt, light, light_alt = utils.get_colorization_colors()
        update_theme(normal, dark, dark_alt, light, light_alt, current_theme)
        player.set_stylesheet(current_theme, normal)

    def handle_theme_change(theme):
        logging.info(f"Handling theme change to: {theme}")
        normal, dark, dark_alt, light, light_alt = utils.get_colorization_colors()
        update_theme(normal, dark, dark_alt, light, light_alt, theme)
        player.set_stylesheet(theme, normal)
        
    if color == "automatic" and platform.system() == "Windows":
        normal, dark, dark_alt, light, light_alt = utils.get_colorization_colors()
        handle_color_change(normal, dark, dark_alt, light, light_alt)

        color_change_listener = ColorChangeListener()
        color_change_listener.color_changed.connect(handle_color_change)
        color_change_listener.start()

        theme_change_listener = ThemeChangeListener()
        theme_change_listener.theme_changed.connect(handle_theme_change)
        theme_change_listener.start()
    else:
        qdt.setup_theme(theme, custom_colors={"primary": clr})
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
