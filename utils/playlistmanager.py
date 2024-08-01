import os
import json
import random

class PlaylistManager:
    def __init__(self):
        self.playlists = {}
        self.shuffle_states = {}
        self.shuffled_songs = {}
        """Initialize PlaylistManager with the directory where playlists are stored."""
        try:
            with open('./config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print("Configuration file not found. Using default settings.")
            config = {"root_playlist_folder": "playlists"}
        except json.JSONDecodeError:
            print("Error decoding the configuration file.")
            config = {"root_playlist_folder": "playlists"}

        self.playlists_dir = config.get('root_playlist_folder', 'playlists')
        # Ensure the playlists directory exists
        if not os.path.exists(self.playlists_dir):
            os.makedirs(self.playlists_dir)
            print(f"Created playlists directory: {self.playlists_dir}")

    def load_playlist(self, playlist_name):
        """Load a playlist by name from the playlists directory."""
        playlist_path = os.path.join(self.playlists_dir, f"{playlist_name}.json")
        
        # Check if the playlist file exists
        if not os.path.isfile(playlist_path):
            raise FileNotFoundError(f"Playlist file not found: {playlist_path}")

        # Load the playlist data
        try:
            with open(playlist_path, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON in playlist file: {playlist_path}")
        except IOError as e:
            raise IOError(f"Error reading playlist file: {playlist_path}") from e

        # Extract playlist name and songs
        playlist_name = data.get("playlist_name", playlist_name)  # Fallback to provided playlist_name
        songs = data.get("songs", [])

        # Store the playlist and reset shuffle states
        self.playlists[playlist_name] = songs
        self.shuffle_states[playlist_name] = False
        self.shuffled_songs[playlist_name] = []

        return playlist_name, songs

    def shuffle_songs(self, playlist_name):
        """Shuffle the songs for a specific playlist."""
        if playlist_name in self.playlists:
            songs = self.playlists[playlist_name][:]
            random.shuffle(songs)
            self.shuffled_songs[playlist_name] = songs
            self.shuffle_states[playlist_name] = True
