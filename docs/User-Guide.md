# User Guide

This guide covers how to use all the features of IotaPlayer.

## Getting Started

### Launching IotaPlayer
1. **Start the application** from your installation
2. **The main window** will open with three main sections:
   - **Left Panel:** Playlist management
   - **Center Panel:** Song list and controls
   - **Right Panel:** Song information and cover art

### Basic Controls
- **Play/Pause:** Click the play button or press media keys
- **Next/Previous:** Use the arrow buttons or media keys
- **Volume:** Adjust with the slider in the left panel
- **Seek:** Drag the progress bar to jump to any point in the song

## Playlist Management

### Loading Playlists
1. **Select a playlist** from the dropdown in the left panel
2. **Click "Load"** to load the selected playlist
3. **Songs will appear** in the center panel

### Creating Playlists
1. **Click "Manage"** to open the Playlist Maker
2. **Choose a method:**
   - **Select Folder:** Add all audio files from a directory
   - **Add Manually:** Enter song details manually
   - **Open Existing:** Edit an existing playlist

### Playlist Controls
- **Reload:** Refresh the playlist list
- **Delete:** Remove the selected playlist
- **Combine:** Merge multiple playlists into one

## Playback Features

### Basic Playback
- **Play/Pause:** Toggle playback with the play button
- **Stop:** Stop playback and reset to beginning
- **Next/Previous:** Skip to next or previous song
- **Seek:** Drag the progress bar to jump to any position

### Advanced Controls
- **Loop:** Toggle between Off, All, and One modes
- **Shuffle:** Randomize the song order
- **Volume:** Adjust from 0% to 100%

### Media Keys
IotaPlayer supports standard media keys:
- **Play/Pause:** `Media Play/Pause` (usually Fn+F7)
- **Next Track:** `Media Next` (usually Fn+F6)
- **Previous Track:** `Media Previous` (usually Fn+F5)

## Song Information

### Displayed Information
The right panel shows:
- **Artist:** Song artist
- **Title:** Song title
- **Album:** Album name
- **Genre:** Music genre
- **Duration:** Current time / total time
- **Cover Art:** Album artwork (if available)

### Cover Art
- **Automatic extraction** from audio files
- **Caching system** for performance
- **1:1 aspect ratio** for uniform display
- **Fallback image** when no cover art is found

## Search Functionality

### Using Search
1. **Type in the search bar** in the center panel
2. **Select search type:**
   - **Artist & Title:** Search both fields
   - **Genre:** Search by music genre
   - **Album:** Search by album name
3. **Results update** in real-time as you type

### Search Tips
- **Case-insensitive** matching
- **Partial matches** are supported
- **Clear search** by deleting text in the search bar

## Settings Configuration

### Opening Settings
- **Click "Settings"** button in the center panel
- **Settings dialog** opens with organized tabs

### General Tab
- **Playlist folder:** Set default playlist directory
- **Default playlist:** Choose startup playlist
- **Volume:** Set default volume level
- **Font:** Choose application font

### Appearance Tab
- **Accent color:** Set custom color or use automatic
- **Dark mode:** Toggle dark/light theme
- **Theme integration:** Use system theme settings

### Discord Tab
- **Enable Discord integration:** Toggle Rich Presence
- **Client ID:** Discord application ID
- **Large image key:** Custom status image
- **Playing status:** Show "Playing" status

### Google Tab
- **Client secret file:** Path to Google API credentials
- **YouTube upload:** Enable playlist upload feature

### Cover Art Tab
- **Cache settings:** Configure cover art caching
- **Extraction options:** Set cover art preferences

## Discord Integration

### Setup
1. **Enable Discord integration** in Settings
2. **Enter your Discord Client ID** (optional)
3. **Save settings** and restart if needed

### Features
- **Rich Presence:** Shows current song in Discord
- **Status updates:** Real-time song information
- **Custom images:** Display playlist artwork
- **Auto-reconnect:** Handles Discord disconnections

## YouTube Integration

### Setup
1. **Get Google API credentials** (see [Google Setup](Google-Setup))
2. **Set client secret file** in Settings > Google
3. **Authenticate** when first using YouTube features

### Features
- **Open YouTube:** Click "Open song on YouTube" button
- **Upload playlists:** Create YouTube playlists from local playlists
- **Video ID support:** Uses embedded YouTube IDs in filenames

### File Naming
For best YouTube integration, name files like:
```
Artist - Title [YouTubeID].mp3
```

## Keyboard Shortcuts

### Playback
- **Space:** Play/Pause
- **Left Arrow:** Previous track
- **Right Arrow:** Next track
- **Up/Down Arrow:** Volume up/down

### Playlist Management
- **Delete:** Remove selected playlist
- **Ctrl+R:** Reload playlists
- **Ctrl+O:** Open playlist maker

### General
- **F1:** Open About dialog
- **Ctrl+Q:** Quit application
- **Ctrl+S:** Open Settings

## Advanced Features

### MPRIS Support (Linux)
- **Desktop integration:** Works with desktop widgets
- **Media controls:** System media keys work
- **Metadata sharing:** Song info available to other apps

### Update System
- **Automatic checks:** Checks for updates on startup
- **In-app updates:** Update directly from the application
- **Version comparison:** Only prompts for newer versions

### Logging
- **Log files:** Check `combined_app.log` for debugging
- **Console output:** Verbose logging available
- **Error tracking:** Detailed error information

## Troubleshooting

### Common Issues
- **Audio not playing:** Check codec support
- **Discord not working:** Verify client ID and permissions
- **YouTube upload fails:** Check Google API setup
- **Cover art missing:** Ensure audio files have embedded artwork

### Getting Help
- **Check logs:** Look in `combined_app.log`
- **Reset settings:** Delete config file to start fresh
- **Report issues:** Use GitHub Issues page

---

**Related Pages:**
- [Configuration](Configuration) - Advanced settings
- [Troubleshooting](Troubleshooting) - Common problems