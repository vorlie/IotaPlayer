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
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Windows":
    ICON_PATH = os.path.join(BASE_DIR, 'icon.ico')
else:
    ICON_PATH = os.path.join(BASE_DIR, 'icon.png')

__version__ = "1.10.13"

default_settings = {
    "connect_to_discord": True,
    "discord_client_id": "1150680286649143356",
    "large_image_key": "default_image",
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


def get_system_qt_version():
    """Get the system's Qt6 version."""
    try:
        # Try qmake6 first
        process = subprocess.run(
            ["qmake6", "-v"],
            capture_output=True, text=True, check=True
        )
        for line in process.stdout.splitlines():
            if line.startswith("Qt version"):
                return line.split()[-1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try dpkg query
        process = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", "libqt6core6"],
            capture_output=True, text=True, check=True
        )
        return process.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try rpm query
        process = subprocess.run(
            ["rpm", "-q", "qt6-qtbase"],
            capture_output=True, text=True, check=True
        )
        version_part = process.stdout.split('-')[2]
        return version_part
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try pacman query
        process = subprocess.run(
            ["pacman", "-Q", "qt6-base"],
            capture_output=True, text=True, check=True
        )
        return process.stdout.split()[-1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None

def get_changelog_entry(version_to_find):
    """
    Fetches the CHANGELOG.md from the repository and returns the entry for the specified version.
    """
    changelog_url = "https://raw.githubusercontent.com/vorlie/IotaPlayer/main/CHANGELOG.md"
    try:
        with urllib.request.urlopen(changelog_url, timeout=5) as response:
            full_changelog = response.read().decode().strip()
    except Exception as e:
        print("Could not fetch changelog:", e)
        return None

    # Split the content by the version headers
    sections = full_changelog.split("## [")

    # Find the section that corresponds to the version we're looking for
    for section in sections:
        if section.startswith(f"{version_to_find}]"):
            # The content of this section is what we want
            # Remove the version and date from the beginning
            content = section.split(" - ", 1)[1]
            return content.strip()

    return "Changelog entry not found for this version."

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
    changelog = get_changelog_entry(latest) if latest else None
    if latest and latest != current_version:
        # Compare versions to ensure latest is actually higher
        if is_version_higher(latest, current_version):
            return True, latest, changelog
    return False, latest, None

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