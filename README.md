# Iota Player

[![ko-fi](https://img.shields.io/badge/kofi-vorlie-%23F16061.svg?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/vorlie)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)
![GitHub top language](https://img.shields.io/github/languages/top/vorlie/IotaPlayer.svg?style=for-the-badge)
[![license](https://img.shields.io/github/license/vorlie/IotaPlayer.svg?style=for-the-badge)](https://github.com/vorlie/IotaPlayer/blob/master/LICENSE) 
![GitHub last commit](https://img.shields.io/github/last-commit/vorlie/IotaPlayer.svg?style=for-the-badge)

[Core Features](#core-features) • [Installation](#installation) • [Configuration](#configuration) • [License](LICENSE) • [Contributing](CONTRIBUTING.md) • [Gallery](#gallery) • [Troubleshooting](#troubleshooting) • [User Interface](#user-interface) • [Shortcuts](#shortcuts) • [Logging](#logging) • [Playlist Maker](#playlist-maker) •
[Usage](#usage)

A feature-rich music player application with playlist management, playback controls, song information display, volume and progress tracking, Discord integration, and more.

## Cover Art Extraction, Caching, and 1:1 Cropping

Iota Player now includes automatic extraction and caching of embedded cover art from your music files. All cover images are processed to a 1:1 (square) aspect ratio by cropping the center, ensuring a consistent and visually appealing display in the player UI.

### How it works
- **Extraction:** Scans your music folders for audio files (MP3, FLAC, OGG, M4A) and extracts embedded cover art.
- **Caching:** Saves processed covers to a local cache for fast access and reduced disk reads.
- **1:1 Cropping:** Crops covers to a perfect square, centered, so all album art displays uniformly without side bars or padding.
- **Threaded:** The extraction and caching process runs in a background thread, so your UI remains responsive.

### How to use
1. **Open Settings:** Go to the Settings dialog in Iota Player.
2. **Navigate to the "Cover Art" Tab:**
   - Click the "Extract & Cache Covers" button to start the process.
   - Progress is shown in a progress bar.
3. **Automatic Usage:**
   - Once covers are cached, the player will automatically use the cached, cropped cover art in the right info frame when displaying song details.
   - If no embedded cover is found, a default image is used.

This feature is cross-platform and works on Windows, Linux, and macOS.

> You might need to restart Iota Player if it doesn't use the cached covers instantly.

## Installation

### Windows
- **Recommended:** Download the latest compiled `.exe` or `.zip` from the [Releases](https://github.com/vorlie/IotaPlayer/releases) page and run/extract it.
- **From source:** Follow the Linux instructions below using Python 3.12+ and all dependencies.

### Linux (and other platforms)
- **No prebuilt binaries provided.** You must install from source due to distro differences.
- **Requires Python 3.12 or newer.**
- **Install dependencies:**
  - Python 3.12 or newer
  - [PyQt5](https://pypi.org/project/PyQt5/), [matplotlib](https://pypi.org/project/matplotlib/), [numpy](https://pypi.org/project/numpy/), [mutagen](https://pypi.org/project/mutagen/), [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/), [pynput](https://pypi.org/project/pynput/)
  - For audio playback: GStreamer and plugins (see below)
- **Example (Ubuntu/Debian):**
  ```sh
  sudo apt update
  sudo apt install python3 python3-pip python3-venv python3-pyqt5 python3-pyqt5.qtmultimedia \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    libxcb-xinerama0
  # Optional: for best performance
  sudo apt install python3-numpy python3-matplotlib
  ```
- **Clone the repository or extract the .zip file:**
  ```sh
  # If using git:
  git clone https://github.com/vorlie/IotaPlayer.git
  cd IotaPlayer
  # If using the .zip, extract and cd into the folder
  ```
- **Create and activate a virtual environment (recommended):**
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Install Python dependencies:**
  ```sh
  pip3 install -r requirements.txt --ignore-requires-python
  ```
  - If you encounter issues, see the [Troubleshooting](#troubleshooting) section for tips and alternative install commands.
- **Run the application:**
  ```sh
  python main.py
  ```

- **Note:**
  - You may need to install additional system packages depending on your distro (see Troubleshooting).
  - If you encounter Qt or GStreamer errors, see the Troubleshooting section below.
  - **Some MP3 files may not play if you do not have the required codecs installed.** On Windows, you may need to install a codec pack such as [K-Lite Codec Pack](https://codecguide.com/download_kl.htm) to enable playback of certain files (especially those with ID3 tags or special encodings). On Linux, ensure you have the full set of GStreamer plugins installed as shown above.
  - If you see errors like `DirectShowPlayerService::doRender: Unresolved error code 80040266`, it usually means a required codec is missing. This error (0x80040266, VFW_E_NO_TRANSPORT) often occurs when the MP3 file contains an overly long ID3 tag section, which the stock decoder cannot skip to reach the audio data. Installing a richer codec pack resolves this issue.

---

## Very Special Thanks!
 - [DarkDetect](https://github.com/albertosottile/darkdetect) for the source code for windows dark mode detection.
    - Where used? [Here](utils/__init__.py) It was used as a base for getting ColorizationColor from the registry.

## Features

### TODO: [Click here](https://github.com/users/vorlie/projects/3/views/1)

### Core Features

- **Playlists Management:**
  - **Load Playlist:** Load playlists from a specified directory.
  - **Reload Playlists:** Refresh the list of available playlists.
  - **Delete Playlist:** Remove a selected playlist.
  - **Create/Edit Playlist:** Use the [Playlist Maker](#playlist-maker) to create or edit playlists.
  - **Combine All Playlists:** Combine all songs from multiple playlists into a single playlist.

- **Music Playback Controls:**
  - **Play/Pause/Resume/Stop:** Start, pause, resume, or stop the currently playing song.
  - **Previous/Next:** Skip to the previous or next song in the playlist.
  - **Loop/Shuffle:** Toggle loop and shuffle modes.
  - **Seek Bar:** Drag the progress bar to seek to any position in the song. Playback and Discord Rich Presence update instantly.
  - **Native PyQt5 Media Player:** Uses QMediaPlayer for improved playback reliability and UI integration.

- **Song Information:**
  - **Display Song Info:** Show details of the currently playing song (artist, title, album, genre).
  - **Update Window Title:** Reflect the current song info and playlist in the window title.

- **Volume Control:**
  - **Adjust Volume:** Change playback volume via a slider.

- **Progress Tracking:**
  - **Track Progress:** Display and update the progress of the currently playing song.
  - **Format Time:** Convert elapsed time and total duration into a readable format.

- **YouTube Integration:**
  - **Upload Playlist to YouTube:** Upload local playlists to your YouTube account (requires Google API setup).
  - **Google Client Secret Path in Settings:** Set the path to your Google API client secret file directly from the app's settings.
  - **Upload Button State:** The YouTube upload button is enabled only when a valid client secret file is set.

- **Discord Integration:**
  - **Update Discord Status:** Display the current song info in Discord status.
  - **Custom Presence Images:** Display custom playlist images in Discord status.
  - **Check Discord Connection:** Monitor and display connection status to Discord.
  - **Rich Presence Sync:** Discord Rich Presence updates instantly when seeking or changing songs.

- **Key Bindings:**
  - **Media Keys:** Handle media keys for play/pause, next, and previous track.

- **External Actions:**
  - **Open YouTube:** Open the YouTube video for the current song, if available.

### User Interface

- **Accent Color:**
  - With the settings page added, you can change most of the settings directly from the application.
  - **Use System Accent Color:** Use the system's accent color. (Windows and macOS only)
    - In order to use the system's accent color, you must set the `automatic` value for the `colorization_color` in the [config.json](config.json#L15) file.
  - **Set your own Accent Color:** Specify the hex color code of the accent color.
    - In order to use your own accent color, you must set the `your_hex_color` value for the `colorization_color` in the [config.json](config.json#L15) file.

- **Playlists and Songs Display:**
  - **Playlist List:** Show available playlists and their song counts.
  - **Song List:** Display the list of songs in the currently loaded playlist.
  - **Song information**: For displaying the currently playing song's artist(s), title, album and genre.

- **Controls and Layouts:**
  - **Control Buttons:** Various buttons for playback control, playlist management, and external actions.
  - **Sliders:** For adjusting volume and tracking song progress.
  - **Labels:** For displaying song info, playback time, and Discord status.

- **Dialogs:**
  - **Open Playlist Dialog:** Select and load playlists.

### Shortcuts

- **Delete Playlist**: Select a playlist and press the `Delete` key to remove it from the list.
  - **Delete Song**: [(From Playlist Maker)](#playlist-maker) Select the song and press the `Delete` key to remove it from the playlist.
- **Play/Pause**: Use the `Media Play/Pause` (`FN + F7`) key to toggle play/pause.
- **Next Track**: Use the `Media Next` (`FN + F6`) key to skip to the next track.
- **Previous Track**: Use the `Media Previous` (`FN + F5`) key to return to the previous track.

### Logging

- **Logging Setup:**
  - **Console Logging:** Output logs to the console.
  - **File Logging:** Save logs to a rotating file for persistent records.

## Playlist Maker

The `PlaylistMaker` class provides a user-friendly interface for creating and managing playlists. It allows users to select folders containing songs, add songs manually, and save playlists in JSON format. 

### Features

- **Select Folder**: Automatically populate the playlist with songs from a selected folder.
- **Add Songs Manually**: Enter song details manually including artist, title, YouTube ID, and song path.
- **Save Playlist**: Save the created playlist in JSON format.
- **Open Existing Playlist**: Load and edit an existing playlist.
- **Edit Songs**: Double-click on a song entry to edit its details.
- **Delete Songs**: Select a song and press the Delete key to remove it.

### How to Use

1. **Select Folder**:
   - Click on the "Select Folder" button to choose a folder containing MP3 files.
   - The application will automatically process the folder and add all MP3 files matching the naming pattern to the playlist.

2. **Add Songs Manually**:
   - Fill in the "Artist", "Title", "YouTube ID" (optional), and "Song Path" fields.
   - Click the "Add Song" button to add the song to the playlist.

3. **Save Playlist**:
   - Enter a name for the playlist in the "Enter playlist name" field.
   - Add a playlist image if you want to. It's optional after all.
   - Click the "Save Playlist" button to save the playlist as a JSON file.

4. **Open Existing Playlist**:
   - Click the "Open Existing Playlist" button to load a playlist.
   - Select the JSON file of the playlist you want to open.

5. **Edit and Delete Songs**:
   - To edit a song, double-click on the corresponding cell in the table.
   - To delete a song, select the row and press the Delete key.

### Naming Scheme

For automatic recognition, the song files in the selected folder should follow this naming scheme:
- **Artist**: The name of the artist.
- **Title**: The title of the song.
- **YouTube ID**: (Optional) The YouTube ID for the song.
    ```
    Artist - Title [YouTube ID].mp3
    ```
    **Example(s)**:
    ```
        Artist - Title [dQw4w9WgXcQ].mp3
        Artist (feat. Artist) - Title (Bass Boosted) [dQw4w9WgXcQ].mp3
    ```

### Example playlist json result

```json
{
    "playlist_name": "default",
    "playlist_large_image_key":"https://i.pinimg.com/236x/42/43/03/424303bef006eb35803ae00505248d7a.jpg",
    "song_count": 2,
    "songs": [
        {
            "artist": "Artist 1",
            "title": "Title 1",
            "youtube_id": "dQw4w9WgXcQ",
            "path": "C:\\Users\\USER\\Music\\FOLDER\\Artist 1 - Title 1 [dQw4w9WgXcQ].mp3",
            "playlist": "default",
            "album": "Album 1",
            "genre": "Genre 2",
            "picture_path": "C:\\Users\\USER\\Music\\FOLDER\\picture.jpg",
            "picture_link":"link to the picture (for rich presence)"
        },
        {
            "artist": "Artist 2",
            "title": "Title 2",
            "youtube_id": "dQw4w9WgXcQ",
            "path": "C:\\Users\\USER\\Music\\FOLDER\\Artist 2 - Title 2 [dQw4w9WgXcQ].mp3",
            "playlist": "default",
            "album": "Album 2",
            "genre": "Genre 2",
            "picture_path": "C:\\Users\\USER\\Music\\FOLDER\\picture.jpg",
            "picture_link":"link to the picture (for rich presence)"
        }
    ]
}
```

## Usage

1. **Run the application:**

    ```bash
    python main.py
    ```
    or use the executable you built in the previous step.
    
2. **Control the application:**
    - Use the UI buttons to control playback, manage playlists, and access external actions.
    - Use media keys on your keyboard to control playback.

3. **Create/Edit Playlists:**
    - Access the Playlist Maker to create or edit playlists.

4. **Discord Integration:**
    - The application will automatically update your Discord status with the current song info if connected.

## Configuration
**With the settings page added, you can change most of the settings directly from the application.**
- **`config.json`:** Place your configuration settings here. Example:
    - If file is not present, application will create it with default values.
    ```json
      {
          "connect_to_discord": true, # disable or enable the RPC
          "discord_client_id": "1150680286649143356",
          "large_image_key": "default_image", # image key or image link
          "use_playing_status": false, # if false, it will use listening type
          "root_playlist_folder": "playlists", # path to the folder
          "default_playlist": "default", # name of the default playlist
          "colorization_color": "automatic", # hex color or leave it as it is, it will use system accent color
          "volume_percantage": 100, # integer value for volume percentage (0-100)
          "google_client_secret_file": "path/to/client_secret.json" # path to your Google API client secret file
      }
    ```

- **Google API Setup:**
    - See [GOOGLE.md](GOOGLE.md) for full instructions on setting up YouTube Data API integration, including how to obtain and configure your client secret file.

- **Logging Configuration:**
    - In `musicPlayer.py` there are commented logging configurations. Uncomment them to use them.
        - Logs are written to `combined_app.log` for application and discord logs.

## Troubleshooting

- **Python version:**
  - This app requires **Python 3.12 or newer**. Check your version with:
    ```sh
    python --version
    # or
    python3 --version
    ```
  - If your version is too old, install Python 3.12+ from your package manager or [python.org](https://www.python.org/downloads/).

- **Ensure all dependencies are installed:**
  - Always refer to `requirements.txt` for the most up-to-date list of dependencies. You can install them with:
    ```sh
    pip install -r requirements.txt --ignore-requires-python
    ```
  - On Linux, also ensure GStreamer and Qt platform plugins are installed (see Installation section above).

- **Qt platform plugin errors (Linux):**
  - If you see errors about `xcb` or Qt platform plugins, install:
    ```sh
    sudo apt install libxcb-xinerama0 libxcb1 libx11-xcb1
    sudo apt install libgl1-mesa-glx
    ```
  - If running under Wayland, try:
    ```sh
    export QT_QPA_PLATFORM=xcb
    python main.py
    ```

- **Check Discord connection:**
  - Ensure your Discord client ID is correct and that you are connected to Discord.

- **Review logs:**
  - Check `combined_app.log` for detailed logging information if issues arise.

- **Other issues:**
  - If you see permission errors with the virtual environment, ensure you own the files and have execute permissions:
    ```sh
    chmod +x venv/bin/activate
    sudo chown -R $USER:$USER venv
    ```
  - For missing system dependencies, refer to your distro’s documentation or the Installation section above.

---

## Gallery

<details>
  <summary>Show Gallery</summary>

  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px;">
    <a href="images/IotaPlayer_MainWindowDark.png"><img src="images/IotaPlayer_MainWindowDark.png" alt="Main Interface Dark" style="width: 350px; height: auto;"></a>
    <a href="images/IotaPlayer_MainWindowLight.png"><img src="images/IotaPlayer_MainWindowLight.png" alt="Main Interface Light" style="width: 350px; height: auto;"></a>
  </div>
  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px;">
    <a href="images/IotaPlayer_PlaylistMakerDark.png"><img src="images/IotaPlayer_PlaylistMakerDark.png" alt="Playlist Maker Dark" style="width: 350px; height: auto;"></a>
    <a href="images/IotaPlayer_PlaylistMakerLight.png"><img src="images/IotaPlayer_PlaylistMakerLight.png" alt="Playlist Maker Light" style="width: 350px; height: auto;"></a>
  </div>
  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px;">
    <a href="images/IotaPlayer_SettingsDark.png"><img src="images/IotaPlayer_SettingsDark.png" alt="Settings Dark" style="width: 350px; height: auto;"></a>
    <a href="images/IotaPlayer_SettingsLight.png"><img src="images/IotaPlayer_SettingsLight.png" alt="Settings Light" style="width: 350px; height: auto;"></a>
  </div>
</details>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Thanks

- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)**: A set of Python bindings for the Qt application framework, which provides the GUI capabilities for this application.
- **[qdarktheme](https://github.com/vorlie/PyQtDarkTheme)**: A library for applying dark themes to PyQt5 applications, enhancing the visual appeal of the interface.
- **[pygame](https://www.pygame.org/)**: A cross-platform set of Python modules designed for writing video games, providing functionality for sound and music.
- **[pypresence](https://pypi.org/project/pypresence/)**: A Python library for integrating with Discord's Rich Presence, allowing you to display custom activity information.
- **[mutagen](https://mutagen.readthedocs.io/en/latest/)**: A Python module used for handling audio metadata, enabling the application to read and write metadata in audio files.
- **[pynput](https://pynput.readthedocs.io/en/latest/)**: A library for controlling and monitoring input devices, such as keyboards and mice.
- **[pyinstaller](https://www.pyinstaller.org/)**: A tool for converting Python applications into stand-alone executables, allowing for easier distribution and deployment.

## Building from source (advanced/optional)
If you want to build a standalone executable (Windows only):

- Install [PyInstaller](https://www.pyinstaller.org/):
  ```sh
  pip install pyinstaller==6.6.0
  ```
- Build:
  ```sh
  pyinstaller IotaPlayerWIN.spec
  ```
- For console output, set `console=True` in the `.spec` file.
