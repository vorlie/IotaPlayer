# Configuration Guide

This guide covers all configuration options available in IotaPlayer.

## Settings Dialog

### Opening Settings
- **Click "Settings"** button in the main interface
- **Settings dialog** opens with organized tabs
- **Changes are saved** automatically when you close the dialog

## General Settings

### Playlist Configuration
- **Root Playlist Folder:** Directory where playlists are stored
  - Default: `playlists/` (relative to app directory)
  - Can be set to any accessible folder path
- **Default Playlist:** Playlist to load on startup
  - Options: Any available playlist name
  - Empty: No playlist loaded on startup

### Volume Settings
- **Default Volume:** Initial volume level (0-100%)
- **Volume Persistence:** Remembers last volume setting
- **Volume Display:** Shows current volume percentage

### Font Settings
- **Font Name:** Application font family
  - Default: "Noto Sans"
  - Can use any system font
- **Font Size:** Text size throughout the application
- **Font Weight:** Bold, normal, or light text

## Appearance Settings

### Theme Configuration
- **Dark Mode:** Toggle between light and dark themes
  - Automatic: Follows system theme
  - Manual: Force light or dark mode
- **Accent Color:** Customize the application accent color
  - Automatic: Uses system accent color
  - Custom: Choose any hex color value
  - Examples: `#ff50aa`, `#4d1833`, `#007acc`

### Color Options
- **Background Color:** Main window background
- **Text Color:** Primary text color
- **Accent Color:** Highlight and button colors
- **Border Color:** Window and element borders

### Theme Integration
- **System Theme:** Automatically match system appearance
- **Custom Theme:** Use IotaPlayer's built-in themes
- **Manual Override:** Force specific theme regardless of system

## Discord Integration

### Basic Setup
- **Enable Discord Integration:** Toggle Rich Presence feature
- **Client ID:** Your Discord application ID
  - Default: `1150680286649143356`
  - Can be customized for personal Discord apps

### Rich Presence Options
- **Large Image Key:** Custom status image
  - Options: `default_image`, `pause`, `play`, `repeat`, `stop`
  - Custom: Any valid Discord image key
- **Playing Status:** Show "Playing" in Discord status
  - On: Shows "Playing IotaPlayer"
  - Off: Shows just the song information

### Advanced Discord Settings
- **Auto-reconnect:** Automatically reconnect if Discord disconnects
- **Status Updates:** Real-time song information updates
- **Custom Images:** Use playlist artwork as status image

## Google Integration

### YouTube API Setup
- **Client Secret File:** Path to Google API credentials
  - Format: JSON file from Google Cloud Console
  - Location: Any accessible file path
- **Authentication:** OAuth 2.0 flow for YouTube access
- **Token Storage:** Automatic token caching in `token.pickle`

### YouTube Features
- **Playlist Upload:** Create YouTube playlists from local playlists
- **Video Opening:** Open YouTube videos for current songs
- **Video ID Support:** Extract YouTube IDs from filenames

### File Naming Convention
For YouTube integration, use this naming format:
```
Artist - Title [YouTubeID].mp3
```
Examples:
- `Artist - Song [dQw4w9WgXcQ].mp3`
- `Artist (feat. Other) - Song [abcdef12345].mp3`

## Cover Art Settings

### Extraction Options
- **Auto-extract:** Automatically extract cover art from audio files
- **Cache Enabled:** Store extracted covers for faster loading
- **Cache Location:** Directory for cover art cache
- **Cache Size:** Maximum cache size in MB

### Display Options
- **Aspect Ratio:** 1:1 (square) for uniform display
- **Quality:** High-quality image processing
- **Fallback Image:** Default image when no cover art found
- **Auto-crop:** Automatically crop covers to square format

### Cache Management
- **Clear Cache:** Remove all cached cover art
- **Cache Statistics:** View cache size and file count
- **Auto-cleanup:** Remove old cache entries automatically

## Advanced Settings

### Logging Configuration
- **Log Level:** Detail level for log messages
  - Options: DEBUG, INFO, WARNING, ERROR
- **Log File:** Location of log file
  - Default: `combined_app.log`
- **Console Output:** Show logs in terminal/console
- **File Rotation:** Automatic log file rotation

### Performance Options
- **Threading:** Use background threads for heavy operations
- **Memory Management:** Optimize memory usage
- **Caching:** Enable various caching mechanisms
- **Background Processing:** Non-blocking UI operations

### Update Settings
- **Auto-check Updates:** Check for updates on startup
- **Update Channel:** Stable or development releases
- **Update Notifications:** Show update prompts
- **Update Path:** Custom update installation directory

## Configuration Files

### File Locations
- **Linux/macOS:** `~/.config/IotaPlayer/config.json`
- **Windows:** `%APPDATA%\IotaPlayer\config.json`

### File Format
Configuration is stored in JSON format:
```json
{
    "connect_to_discord": true,
    "discord_client_id": "1150680286649143356",
    "large_image_key": "default_image",
    "use_playing_status": false,
    "root_playlist_folder": "playlists",
    "default_playlist": "default",
    "colorization_color": "automatic",
    "volume_percentage": 100,
    "google_client_secret_file": "path/to/client_secret.json"
}
```

### Manual Configuration
You can edit the config file directly:
1. **Close IotaPlayer** completely
2. **Edit the config file** with a text editor
3. **Save the file** and restart IotaPlayer
4. **Verify settings** in the Settings dialog


## Troubleshooting Configuration

### Common Issues
- **Settings not saving:** Check file permissions
- **Config file corrupted:** Delete and restart
- **Theme not applying:** Restart application
- **Discord not working:** Verify client ID

### Reset Configuration
To reset all settings:
1. **Close IotaPlayer**
2. **Delete the config file**
3. **Restart the application**
4. **Reconfigure settings** as needed

### Backup Configuration
To backup your settings:
1. **Copy the config file** to a safe location
2. **Note the file path** for restoration
3. **Restore by copying back** when needed

---

**Related Pages:**
- [User Guide](User-Guide) - How to use features
- [Troubleshooting](Troubleshooting) - Solve problems