# core/google.py
"""
YouTube Data API authentication and playlist management for IotaPlayer.

Features:
- Authenticates with YouTube Data API v3 using OAuth 2.0.
- Creates YouTube playlists and adds videos to them.
- Saves OAuth tokens to 'token.pickle' for reuse (avoids repeated logins).

Requirements:
- You must have a client secrets file (usually named 'client_secret.json') downloaded from the Google Cloud Console:
  https://console.cloud.google.com
- Enable the YouTube Data API v3 for your project in the Google Cloud Console.
- Place your client secrets file in the same directory as this script, or provide its absolute path in CLIENT_SECRETS_FILE.

Usage Example:
    Set CLIENT_SECRETS_FILE = 'client_secret.json' (or your file path).
    service = get_authenticated_service()
    playlist_id = create_youtube_playlist(service, 'My Playlist')
    add_videos_to_youtube_playlist(service, playlist_id, ['dQw4w9WgXcQ'])

Functions:
- get_authenticated_service(): Handles OAuth and returns an authenticated YouTube API service object.
- create_youtube_playlist(service, title, ...): Creates a new playlist.
- add_videos_to_youtube_playlist(service, playlist_id, video_ids): Adds videos to a playlist.
"""
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import json

# Define the scopes required for playlist management
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = "" # Path to your client secrets file (JSON)
# This file should be created in the same directory as this script or provide an absolute path
TOKEN_PICKLE_FILE = "token.pickle"

def load_client_secrets_path():
    """Load the client secret file path from config.json."""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("google_client_secret_file", "")
    return ""

def get_authenticated_service():
    """Gets an authenticated YouTube Data API service object. Handles OAuth flow."""
    global CLIENT_SECRETS_FILE
    CLIENT_SECRETS_FILE = load_client_secrets_path()
    if not CLIENT_SECRETS_FILE or not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"ERROR: Client secrets file not found at {CLIENT_SECRETS_FILE}")
        return None

    creds = None
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