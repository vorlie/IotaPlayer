import sys
import json
import os
import qdarktheme as qdt
from PyQt5.QtWidgets import QApplication
from core.musicPlayer import MusicPlayer
from core.logger import setup_logging
from config import ICON_PATH

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

def main():
    qdt.enable_hi_dpi()
    app = QApplication(sys.argv)
    config = load_config(CONFIG_PATH)
    qdt.setup_theme("auto")
    
    default_settings = {   
        "connect_to_discord_comment": "Connect to Discord? If set to true, application will try to connect to discord in order to set your presence. Set it to false if you don't want to connect to Discord. The default value is 'true'.",
        "connect_to_discord": True,
        "discord_client_id_comment": "Enter your Discord Client ID. You can find it in your Discord Developer Portal. You can modify this ID as required. It will be used to connect to Discord and will change the name of the application that's seen in Discord. The default value is '1150680286649143356'.",
        "discord_client_id": "1150680286649143356",
        "large_image_key_comment": "Enter the name of the large image key. You can use links. You can modify this key as required. The default value is 'large_image_key'.",
        "large_image_key": "https://i.pinimg.com/564x/d5/ed/93/d5ed93e12eab198b830bc91f1ddf2dcb.jpg",
        "root_playlist_folder_comment": "Specify the directory where your playlists are saved. You can change this path if needed. The default value is 'playlists'.",
        "root_playlist_folder": "playlists",
        "default_playlist_comment": "Enter the name of the default playlist that will be loaded initially. You can modify this name as required.",
        "default_playlist": "default",
        "colorization_color_comment": "Enter the hex color code of the accent color. You can modify this color as required. The default value is 'automatic'. Which will use the system's colorization color.",
        "colorization_color": "automatic"
    }
    
    player = MusicPlayer(settings=default_settings, icon_path=ICON_PATH)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()