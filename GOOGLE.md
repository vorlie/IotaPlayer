## YouTube Data API Integration for IotaPlayer

This document explains how to set up and use YouTube Data API features in IotaPlayer, including authentication, playlist creation, and adding videos to playlists.

---

## Features

- Authenticate with the YouTube Data API v3 using OAuth 2.0.
- Create YouTube playlists and add videos to them from IotaPlayer.
- Save OAuth tokens to `token.pickle` for reuse (avoids repeated logins).

---

## Requirements

1. **Google Cloud Project**
   - Go to the [Google Cloud Console](https://console.cloud.google.com).
   - Create a new project or select an existing one.

2. **Enable YouTube Data API v3**
   - In your project, navigate to "APIs & Services" > "Library".
   - Search for "YouTube Data API v3" and enable it.

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "OAuth client ID".
   - Choose "Desktop app" as the application type.
   - Download the `client_secret.json` file.

4. **Configure IotaPlayer**
   - Place your `client_secret.json` file somewhere on your computer.
   - In IotaPlayer, open Settings > Google tab.
   - Set the "Client Secret File" path to your `client_secret.json` file.
   - Save and restart IotaPlayer.

---

## Usage

### First-Time Authentication

- When you use a YouTube feature for the first time (such as uploading a playlist), IotaPlayer will prompt you to authenticate.
- A browser window will open. Log in with your Google account and grant the requested permissions.
- After successful authentication, a `token.pickle` file will be created and reused for future API calls.

### Example Python Usage

```python
from core.google import get_authenticated_service, create_youtube_playlist, add_videos_to_youtube_playlist

service = get_authenticated_service()
playlist_id = create_youtube_playlist(service, 'My Playlist')
add_videos_to_youtube_playlist(service, playlist_id, ['dQw4w9WgXcQ'])
```

---

## Functions

- **get_authenticated_service()**  
  Handles OAuth and returns an authenticated YouTube API service object.

- **create_youtube_playlist(service, title, ...)**  
  Creates a new playlist on YouTube.

- **add_videos_to_youtube_playlist(service, playlist_id, video_ids)**  
  Adds a list of video IDs to a YouTube playlist.

---

## Troubleshooting

- If you see an error about a missing or invalid client secret file, double-check the path in your settings and ensure the file exists.
- If authentication fails, try deleting `token.pickle` and re-authenticating.
- Make sure your Google account has access to YouTube and the API is enabled for your project.

---

## Security

- Keep your `client_secret.json` file private. Do not share it or commit it to public repositories.
- The `token.pickle` file contains your OAuth tokens. Treat it as sensitive data.

---

If you follow these steps, you’ll be able to use YouTube integration features in IotaPlayer!