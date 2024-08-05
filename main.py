# main.py
import qdarktheme as qdt, sys, json, platform, logging
from utils import _detect_windows_theme
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from config import ICON_PATH, default_settings

setup_logging()

CONFIG_PATH = "config.json"
DEFAULT_ACCENT_COLOR = "#ff50aa"

class ColorChangeListener(QThread):
    color_changed = pyqtSignal(str)
    
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

    def run(self):
        _detect_windows_theme.listener(self.on_color_change)

    def on_color_change(self, color):
        logging.info("System color change detected: " + color)
        self.color_changed.emit(color)
        
def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config: {e}")
        return default_settings

def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    player = MusicPlayer(settings=default_settings, icon_path=ICON_PATH, config_path=CONFIG_PATH)
    player.show()

    config = load_config()
    color = config.get("colorization_color", "automatic")

    if platform.system() == "Windows": # Windows only
        if color == "automatic": # Use the system's accent color
            qdt.setup_theme("auto") # Set the default accent color
            color_change_listener = ColorChangeListener()
            color_change_listener.color_changed.connect(lambda color: qdt.setup_theme('auto', custom_colors={"primary": color}))
            color_change_listener.start() # Start listening for system color changes
        else:    
            qdt.setup_theme('auto', custom_colors={"primary": color})
    elif platform.system() == "Darwin": # macOS only
        if color == "automatic": # Use the system's accent color
            qdt.setup_theme("auto")
        else:
            qdt.setup_theme(custom_colors={"primary": color})
    else: # Other platforms
        if color == "automatic": # Use the default accent color
            qdt.setup_theme("auto", custom_colors={"primary": DEFAULT_ACCENT_COLOR})
        else:
            qdt.setup_theme(custom_colors={"primary": color})
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
