import qdarktheme as qdt
import sys
import json
import platform
import logging
import utils
import darkdetect
from time import sleep
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtGui import QIcon
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from config import ICON_PATH, default_settings

setup_logging()

CONFIG_PATH = "config.json"
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
        import ctypes
        from ctypes.wintypes import HWND
            
        hwnd = int(player.winId())
        logging.info(f"Windows HWND: {hwnd}")
        SW_RESTORE = 9
        ctypes.windll.user32.ShowWindow(HWND(hwnd), SW_RESTORE)
        ctypes.windll.user32.SetForegroundWindow(HWND(hwnd))
        ctypes.windll.user32.SetFocus(HWND(hwnd))


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

    clr = utils.get_colorization_colors()[0]
    global player
    player = MusicPlayer(settings=default_settings, icon_path=ICON_PATH, config_path=CONFIG_PATH, theme=darkdetect.theme().lower(), normal=clr)
    player.show()
    player.adjust_volume(player.get_volume)
    config = load_config()
    color = config.get("colorization_color", "automatic")
    tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), app)
    tray_icon.show()
    tray_menu = QMenu()
    
    open_action = QAction("Open", tray_menu)
    open_action.triggered.connect(player.show)
    tray_menu.addAction(open_action)
    
    minimize_action = QAction("Minimize", tray_menu)
    minimize_action.triggered.connect(player.hide)
    tray_menu.addAction(minimize_action)
    
    quit_action = QAction("Quit", tray_menu)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    minimize_to_tray = config.get("minimize_to_tray", False)

    if minimize_to_tray:
        minimize_action.triggered.connect(player.hide)
    else:
        minimize_action.triggered.connect(player.setVisible)
    
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
        
    if color == "automatic":  # Use the system's accent color
        normal, dark, dark_alt, light, light_alt = utils.get_colorization_colors()
        handle_color_change(normal, dark, dark_alt, light, light_alt)  # Initialize with the correct theme

        color_change_listener = ColorChangeListener()
        color_change_listener.color_changed.connect(handle_color_change)
        color_change_listener.start()

        theme_change_listener = ThemeChangeListener()
        theme_change_listener.theme_changed.connect(handle_theme_change)
        theme_change_listener.start()
    else:
        qdt.setup_theme('auto', custom_colors={"primary": color})
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
