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

# core/google.py
# =============
# This module provides Google/YouTube Data API 
# integration for IotaPlayer, including authentication, 
# playlist creation, and adding videos to playlists
# =============
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from core.configManager import ConfigManager

# Define the scopes required for playlist management
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = "" # This will be set later, do not set manually

def get_token_pickle_file():
    """Get the path to the token pickle file."""
    config_manager = ConfigManager.get_instance()
    return os.path.join(config_manager.get_config_dir(), "token.pickle")

def load_client_secrets_path():
    """Load the client secret file path from config.json."""
    config_manager = ConfigManager.get_instance()
    config = config_manager.load_config()
    return config.get("google_client_secret_file", "")

def get_authenticated_service():
    """Gets an authenticated YouTube Data API service object. Handles OAuth flow."""
    global CLIENT_SECRETS_FILE
    CLIENT_SECRETS_FILE = load_client_secrets_path()
    if not CLIENT_SECRETS_FILE or not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"ERROR: Client secrets file not found at {CLIENT_SECRETS_FILE}")
        return None

    creds = None
    TOKEN_PICKLE_FILE = get_token_pickle_file()
    # Load saved credentials if they exist
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token) # Load pickled credentials

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}") # Log appropriately
                creds = None # Force re-authentication
        # If refresh failed or no token exists, start the flow
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0) # Opens browser, user auths, returns creds
            except FileNotFoundError:
                print(f"ERROR: Client secrets file not found at {CLIENT_SECRETS_FILE}")
                return None
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                return None

        # Save the credentials for the next run
        os.makedirs(os.path.dirname(TOKEN_PICKLE_FILE), exist_ok=True)
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token) # Save pickled credentials

    try:
      service = build('youtube', 'v3', credentials=creds)
      return service
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        # Potentially delete the token file if credentials are bad
        # os.remove(TOKEN_PICKLE_FILE)
        return None


def create_youtube_playlist(service, title, description="Created using IotaPlayer", privacy_status="public"):
    """Creates a new YouTube playlist."""
    if not service:
      raise ValueError("YouTube service object is not valid.")
    try:
      request = service.playlists().insert(
          part="snippet,status",
          body={
            "snippet": {
              "title": title,
              "description": description,
            },
            "status": {
              "privacyStatus": privacy_status # 'public', 'private', 'unlisted'
            }
          }
      )
      response = request.execute()
      print(f"Created playlist: {response['snippet']['title']} (ID: {response['id']})")
      return response['id']
    except Exception as e:
        print(f"Error creating playlist '{title}': {e}")
        raise e # Let the caller handle it

def add_videos_to_youtube_playlist(service, playlist_id, video_ids):
    """Adds a list of video IDs to a YouTube playlist."""
    if not service:
        raise ValueError("YouTube service object is not valid.")
    if not playlist_id:
        raise ValueError("Playlist ID is required.")

    added_count = 0
    errors = []
    for video_id in video_ids:
        try:
            request = service.playlistItems().insert(
                part="snippet",
                body={
                  "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                      "kind": "youtube#video",
                      "videoId": video_id
                    }
                  }
                }
            )
            request.execute()
            added_count += 1
            print(f"Added video {video_id} to playlist {playlist_id}")
        except Exception as e:
            print(f"Error adding video {video_id} to playlist {playlist_id}: {e}")
            errors.append(f"{video_id}: {e}")

    return added_count, errors