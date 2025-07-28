import os
import platform
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Windows":
    ICON_PATH = os.path.join(BASE_DIR, 'icon.ico')
else:
    ICON_PATH = os.path.join(BASE_DIR, 'icon.png')

__version__ = "1.10.1"

default_settings = {
    "connect_to_discord": True,
    "discord_client_id": "1150680286649143356",
    "large_image_key": "default_image",
    "use_playing_status": False,
    "root_playlist_folder": "playlists",
    "default_playlist": "default",
    "colorization_color": "automatic",
    "volume_percentage": 100,
    "font_name": "Noto Sans",
}

discord_cdn_images = {
    "default_image":"https://cdn.discordapp.com/app-assets/1150680286649143356/1270124442433097780.png",
    "pause":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119846850754.png",
    "play": "https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119691661343.png",
    "repeat":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119913959444.png",
    "repeat-one":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119733346315.png",
    "stop":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273717793455603743.png"
}

def get_latest_version():
    url = "https://raw.githubusercontent.com/vorlie/IotaPlayer/main/latest_version.txt"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode().strip()
    except Exception as e:
        print("Could not check for updates:", e)
        return None

def is_update_available(current_version):
    latest = get_latest_version()
    if latest and latest != current_version:
        return True, latest
    return False, latest