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
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from tkinter import Tk, filedialog

def get_audio_metadata(file_path):
    try:
        audio = MP3(file_path, ID3=EasyID3)
        return {
            "artist": audio.get("artist", ["Unknodwn Artist"])[0],
            "title": audio.get("title", [os.path.basename(file_path)])[0],
            "genre": audio.get("genre", [""])[0],
            "album": audio.get("album", ["Unknown Album"])[0],
            "path": file_path.replace("\\", "/")
        }
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")
        return None

def select_directory():
    root = Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Music Directory")

def generate_playlist(directory):
    playlist = {
        "playlist_name": os.path.basename(directory),
        "playlist_large_image_key": "",
        "song_count": 0,
        "songs": []
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                metadata = get_audio_metadata(file_path)
                if metadata:
                    metadata["picture_path"] = ""
                    metadata["picture_link"] = ""
                    metadata["youtube_id"] = ""
                    playlist["songs"].append(metadata)
    
    playlist["song_count"] = len(playlist["songs"])
    return playlist

def save_playlist(playlist, output_file="playlist.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(playlist, f, indent=4)
    print(f"Playlist saved as {output_file}")

if __name__ == "__main__":
    music_dir = select_directory()
    if music_dir:
        playlist_data = generate_playlist(music_dir)
        save_playlist(playlist_data)
    else:
        print("No directory selected.")
