import qdarktheme as qdt, sys, json, platform, logging
import utils, darkdetect
from time import sleep
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QThread, pyqtSignal
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

def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    clr = utils.get_colorization_colors()[0]
    player = MusicPlayer(settings=default_settings, icon_path=ICON_PATH, config_path=CONFIG_PATH, theme=darkdetect.theme().lower(), normal=clr)
    player.show()

    config = load_config()
    color = config.get("colorization_color", "automatic")
    
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
        
    if platform.system() == "Windows":  # Windows only
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
    elif platform.system() == "Darwin":  # macOS only
        if color == "automatic":  # Use the system's accent color
            qdt.setup_theme("auto")
        else:
            qdt.setup_theme(custom_colors={"primary": color})
    else:  # Other platforms
        if color == "automatic":  # Use the default accent color
            qdt.setup_theme("auto", custom_colors={"primary": DEFAULT_ACCENT_COLOR})
        else:
            qdt.setup_theme(custom_colors={"primary": color})
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
