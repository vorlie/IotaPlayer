import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, 'icon.ico')

default_settings = {
    "connect_to_discord": True,
    "discord_client_id": "1150680286649143356",
    "large_image_key": "default_image",
    "use_playing_status": False,
    "root_playlist_folder": "playlists",
    "default_playlist": "default",
    "colorization_color": "automatic",
    "volume_percantage": 100,
    "minimize_to_tray": False,
}

discord_cdn_images = {
    "default_image":"https://cdn.discordapp.com/app-assets/1150680286649143356/1270124442433097780.png",
    "pause":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119846850754.png",
    "play": "https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119691661343.png",
    "repeat":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119913959444.png",
    "repeat-one":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273715119733346315.png",
    "stop":"https://cdn.discordapp.com/app-assets/1150680286649143356/1273717793455603743.png"
}