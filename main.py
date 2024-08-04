# main.py
import qdarktheme as qdt, sys, os, json, platform
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QThread, QTimer
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from config import ICON_PATH

setup_logging()

CONFIG_PATH = "config.json"
DEFAULT_ACCENT_COLOR = "#ff50aa"
default_settings = {
    "connect_to_discord_comment": {
        "1":"Connect to Discord? If set to true, application will try to connect to discord in order to set your presence.",
        "2":"Set it to false if you don't want to connect to Discord.",
        "3":"The default value is 'true'."
    },
    "connect_to_discord": True,
        
    "root_playlist_folder_comment": {
        "1":"Specify the directory where your playlists are saved. You can change this path if needed.", 
        "2": "The default value is 'playlists'."
    },
    "root_playlist_folder": "C:\\Users\\karol\\Music\\",

    "default_playlist_comment": "Enter the name of the default playlist that will be loaded initially. You can modify this name as required.",
    "default_playlist": "default",

    "colorization_color_comment": {
        "1": "Enter the hex color code of the accent color. You can modify this color as required.",
        "2": "If set to 'automatic' the application will use the system's accent color.",
        "3": "The default value is 'automatic'."
    },
    "colorization_color": "automatic",

    "auto_color_interval_comment": {
        "1": "Enter the interval in seconds at which the automatic color will change.",
        "2": "If you find that application is using too much resources (CPU mostly), you can increase this value. 1000 is 1 second, 10000 is 10 seconds, etc.",
        "3": "If you do increase, just so you know that it will have a bit of delay to change the color :)",
        "4": "The default value is '1000'."
    },
    "auto_color_interval": 1000
}

class AccentThread(QThread):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._load_config()
        self.timer = QTimer()
        self.timer.timeout.connect(self.accent)
        self.timer.start(self.interval)

    def _load_config(self) -> None:
        """Load the configuration for the color and interval."""
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            self.interval = config.get("auto_color_interval", 1000)
            self.colorization_color = config.get("colorization_color", "automatic")
        except (FileNotFoundError, json.JSONDecodeError):
            self.interval = 1000
            self.colorization_color = "automatic"

    def accent(self) -> None:
        """Set the application's accent color."""
        if self.colorization_color != "automatic":
            qdt.setup_theme(custom_colors={"primary": self.colorization_color})
            return
        
        if platform.system() in ["Windows", "Darwin"]:  # Windows and macOS
            qdt.setup_theme("auto")
        else:
            qdt.setup_theme(custom_colors={"primary": DEFAULT_ACCENT_COLOR})

    def run(self) -> None:
        self.exec_()

def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdt.setup_theme("auto",custom_colors={"primary": DEFAULT_ACCENT_COLOR}) # Default theme setup
    
    player = MusicPlayer(settings=default_settings, icon_path=ICON_PATH, config_path=CONFIG_PATH)
    player.show()

    accent_thread = AccentThread()
    accent_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
