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

import os
import platform
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Windows":
    ICON_PATH = os.path.join(BASE_DIR, 'icon.ico')
else:
    ICON_PATH = os.path.join(BASE_DIR, 'icon.png')

__version__ = "1.10.8"

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
        # Compare versions to ensure latest is actually higher
        if is_version_higher(latest, current_version):
            return True, latest
    return False, latest

def is_version_higher(version1, version2):
    """
    Compare two version strings and return True if version1 is higher than version2.
    Supports semantic versioning (e.g., "1.2.3", "1.10.5").
    """
    def version_to_tuple(version):
        # Split version string and convert to integers
        parts = version.split('.')
        # Pad with zeros if needed (e.g., "1.2" becomes [1, 2, 0])
        while len(parts) < 3:
            parts.append('0')
        # Convert to integers, handling any non-numeric parts
        try:
            return tuple(int(part) for part in parts[:3])
        except ValueError:
            # If version format is invalid, treat as lower
            return (0, 0, 0)
    
    v1_tuple = version_to_tuple(version1)
    v2_tuple = version_to_tuple(version2)
    
    return v1_tuple > v2_tuple