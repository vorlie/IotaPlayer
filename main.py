import sys
import json
import os
import qdarktheme as qdt
from PyQt5.QtWidgets import QApplication
from core.musicplayer import MusicPlayer
from core.logger import setup_logging

setup_logging()

CONFIG_PATH = "config.json"
DEFAULT_ACCENT_COLOR = "#ff50aa"

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file '{config_path}' not found. Using default settings.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{config_path}'. Using default settings.")
        return {}

def get_system_accent_color():
    """Retrieve the system's accent color from the registry."""
    if os.name == "nt":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            
            colorization_color = winreg.QueryValueEx(key, "ColorizationColor")[0]
            
            winreg.CloseKey(key)
            
            red = (colorization_color >> 16) & 0xFF
            green = (colorization_color >> 8) & 0xFF
            blue = colorization_color & 0xFF
            
            accent_color_hex = '#{:02X}{:02X}{:02X}'.format(red, green, blue)
            
            return accent_color_hex
        except FileNotFoundError:
            print("Registry key not found. Using default accent color.")
            return DEFAULT_ACCENT_COLOR
        except Exception as e:
            print(f"An error occurred while accessing the registry: {e}")
            return DEFAULT_ACCENT_COLOR
    else:
        print("Unsupported operating system. Using default accent color.")
        return DEFAULT_ACCENT_COLOR

def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    config = load_config(CONFIG_PATH)
    accent_color = config.get("colorization_color", "automatic")
    
    if accent_color == "automatic":
        accent_color = get_system_accent_color()
    print(f"Using accent color: {accent_color}")
    qdt.setup_theme(custom_colors={"primary": accent_color})
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()