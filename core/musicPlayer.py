import os, webbrowser, threading, logging, json, re, time, darkdetect
from PyQt5.QtWidgets import ( QMainWindow, 
    QVBoxLayout, QWidget, QPushButton, QListWidget, 
    QFileDialog, QLabel, QSlider, QHBoxLayout, QSizePolicy, 
    QSpacerItem, QMessageBox )
from utils import hex_to_rgba
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
from pygame import mixer
from pynput import keyboard
from mutagen.mp3 import MP3
from core.discordIntegration import DiscordIntegration
from core.playlistMaker import PlaylistMaker, PlaylistManager
from core.settingManager import SettingsDialog
from core.logger import setup_logging

class MusicPlayer(QMainWindow):
    def __init__(self, settings, icon_path, config_path, theme, normal):
        super().__init__()
        self.icon_path = icon_path
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Iota Player • Music Player")
        self.setMinimumSize(800, 600)
    
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = settings
            print(settings)
            try:
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=4)
            except IOError as e:
                print(f"Error writing to config file: {e}")
            try:
                with open('config.json', 'r') as f:
                    self.config = json.load(f)
            except IOError as e:
                print(f"Error reading from config file: {e}")
        playlist_folder = self.config.get('root_playlist_folder', "playlists")
        if not os.path.exists(playlist_folder):
            os.makedirs(playlist_folder)
            logging.info(f"Created playlist folder: {playlist_folder}")
            
        self.initUI()
        self.set_stylesheet(theme, normal)
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.start()
        self.playlist_manager = PlaylistManager()
        self.discord_integration = DiscordIntegration()
        self.settings_manager = SettingsDialog(settings, icon_path, config_path)
        self.discord_integration.connection_status_changed.connect(self.update_discord_status)
        self.current_playlist_image = None
        self.current_song = None
        self.songs = []
        self.song_index = 0
        self.is_looping = "Off"
        logging.info(f"Initialized Iota Player with is_looping = {self.is_looping}")
        self.is_playing = False
        logging.info(f"Initialized Iota Player with is_playing = {self.is_playing}")
        self.is_shuffling = False
        self.shuffled_index = 0
        logging.info(f"Initialized Iota Player with is_shuffling = {self.is_shuffling}; shuffled_index = {self.shuffled_index}")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)
        
        self.check_end_timer = QTimer()
        self.check_end_timer.timeout.connect(self.check_song_end)
        self.check_end_timer.start(100)

        # Timer for checking Discord connection status
        self.connection_check_timer = QTimer()
        self.connection_check_timer.timeout.connect(self.check_discord_connection)
        self.connection_check_timer.start(10000)  # Check every 10 seconds

        mixer.init()
        mixer.music.set_endevent(1)
        self.on_start()
        self.has_started = False
        self.is_paused = False
        
    def set_stylesheet(self, theme, normal):
        if theme == 'dark':
            stylesheet = f"""
                QPushButton {{
                    color: #FFFFFF;
                }}
                QListWidget {{
                    background-color: {hex_to_rgba(normal, 0.1)};
                }}
            """
        else:  # Light mode
            stylesheet = f"""
                QPushButton {{
                    color: #000000;
                }}
                QListWidget {{
                    background-color: {hex_to_rgba(normal, 0.1)};
                }}
                
            """
        self.setStyleSheet(stylesheet)
        
    def initUI(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()  # Changed to vertical layout
        self.central_widget.setLayout(self.main_layout)

        # Top Layout: Left Frame (Playlist) and Right Frame (Song List)
        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout)

        # Left Frame Layout (Playlist controls)
        self.left_frame = QWidget()
        self.left_frame_layout = QVBoxLayout()
        self.left_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.left_frame_layout.setSpacing(10)
        self.left_frame.setLayout(self.left_frame_layout)
        self.left_frame.setFixedWidth(300)
        self.top_layout.addWidget(self.left_frame, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.left_frame_scnd_layout = QHBoxLayout()
        self.left_frame_layout.addLayout(self.left_frame_scnd_layout)

        # Playlist List and Controls Layout
        self.playlist_list_layout = QVBoxLayout()
        self.playlist_list_label = QLabel("Playlists:")
        self.playlist_maker_button = QPushButton("Manage")
        self.playlist_maker_button.setFixedWidth(70)
        self.left_frame_scnd_layout.addWidget(self.playlist_list_label)
        self.left_frame_scnd_layout.addWidget(self.playlist_maker_button)
        self.left_frame_layout.addLayout(self.playlist_list_layout)

        # Playlist List
        self.playlist_list = QListWidget()
        playlists = self.get_playlist_names()
        for name, _, count, _ in playlists:
            self.playlist_list.addItem(f"{name} ({count} Songs)")
        self.playlist_list.currentItemChanged.connect(self.load_playlist_from_list)
        self.playlist_list_layout.addWidget(self.playlist_list)

        # Playlist Controls
        self.playlist_control_label = QLabel("Playlist Controls:")
        self.playlist_list_layout.addWidget(self.playlist_control_label)
        
        self.three_button_layout = QHBoxLayout()
        self.two_button_layout = QHBoxLayout()
        self.one_button_layout = QHBoxLayout()
        
        self.playlist_list_layout.addLayout(self.three_button_layout)
        self.playlist_list_layout.addLayout(self.two_button_layout)
        self.playlist_list_layout.addLayout(self.one_button_layout)

        self.load_button = QPushButton("Load")
        self.reload_button = QPushButton("Reload")
        self.delete_button = QPushButton("Delete")
        self.shuffle_button = QPushButton("Shuffle Off")
        self.loop_button = QPushButton("Loop Off")
        self.youtube_button = QPushButton("Open current song on Youtube")

        self.three_button_layout.addWidget(self.load_button)
        self.three_button_layout.addWidget(self.reload_button)
        self.three_button_layout.addWidget(self.delete_button)
        self.two_button_layout.addWidget(self.shuffle_button)
        self.two_button_layout.addWidget(self.loop_button)
        self.one_button_layout.addWidget(self.youtube_button)

        # Right Frame Layout (Song List)
        self.right_frame = QWidget()
        self.right_frame_layout = QVBoxLayout()
        self.right_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.right_frame_layout.setSpacing(10)
        self.right_frame.setLayout(self.right_frame_layout)
        self.top_layout.addWidget(self.right_frame)
        self.right_frame_scnd_layout = QHBoxLayout()
        self.right_frame_layout.addLayout(self.right_frame_scnd_layout)
        
        # Song List, Settings
        self.song_list_label = QLabel("Song List:")
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedWidth(70)
        self.right_frame_scnd_layout.addWidget(self.song_list_label)
        self.right_frame_scnd_layout.addWidget(self.settings_button)
        self.song_list = QListWidget()
        self.song_list.currentItemChanged.connect(self.play_selected_song)
        self.right_frame_layout.addWidget(self.song_list)
        

        # Bottom Layout: Music Control, Progress, Volume
        self.bottom_layout = QVBoxLayout()
        self.main_layout.addLayout(self.bottom_layout)

        # Music Control Buttons
        self.music_control_layout = QHBoxLayout()
        self.music_control_layout.setContentsMargins(0, 0, 0, 0)
        self.music_control_layout.setSpacing(10)

        # Add a left spacer
        self.left_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.music_control_layout.addItem(self.left_spacer)

        # Create buttons
        self.prev_button = QPushButton("Previous")
        self.toggle_pause_button = QPushButton("Pause")  # Toggle Pause/Resume
        self.toggle_play_button = QPushButton("Play")    # Toggle Play/Stop
        self.next_button = QPushButton("Next")

        # Set fixed width for buttons
        button_width = 70
        self.prev_button.setFixedWidth(button_width)
        self.toggle_pause_button.setFixedWidth(button_width)
        self.toggle_play_button.setFixedWidth(button_width)
        self.next_button.setFixedWidth(button_width)

        # Add buttons to layout
        self.music_control_layout.addWidget(self.prev_button)
        self.music_control_layout.addWidget(self.toggle_pause_button)
        self.music_control_layout.addWidget(self.toggle_play_button)
        self.music_control_layout.addWidget(self.next_button)

        # Add a right spacer
        self.right_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.music_control_layout.addItem(self.right_spacer)

        # Add layout to the bottom layout or your main layout
        self.bottom_layout.addLayout(self.music_control_layout)
        
        # Song Info, Progress and Volume
        self.info_layout = QHBoxLayout()
        self.center_sil_layout = QHBoxLayout()
        
        # Centered song info label
        self.bottom_layout.addLayout(self.center_sil_layout)
        self.song_info_label = QLabel("No song playing")
        self.song_info_label.setAlignment(Qt.AlignCenter)
        self.center_sil_layout.addWidget(self.song_info_label)
        
        self.bottom_layout.addLayout(self.info_layout)
        self.time_label = QLabel("00:00 / 00:00")
        self.info_layout.addWidget(self.time_label)

        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.info_layout.addWidget(self.progress_bar)

        self.volume_label = QLabel("Volume:")
        self.info_layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)  # Start with full volume
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setSingleStep(1)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        self.info_layout.addWidget(self.volume_slider)

        self.discord_status_label = QLabel("Discord Status: Disconnected")
        self.bottom_layout.addWidget(self.discord_status_label)

        # Connect buttons
        self.toggle_play_button.clicked.connect(self.toggle_play)
        self.toggle_pause_button.clicked.connect(self.toggle_pause)
        self.next_button.clicked.connect(self.next_song)
        self.prev_button.clicked.connect(self.prev_song)
        self.load_button.clicked.connect(self.load_playlist_dialog)
        self.loop_button.clicked.connect(self.toggle_loop)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.youtube_button.clicked.connect(self.open_youtube)
        self.reload_button.clicked.connect(self.reload_playlists)
        self.delete_button.clicked.connect(self.delete_playlist)
        self.playlist_maker_button.clicked.connect(self.open_playlist_maker)
        self.settings_button.clicked.connect(self.open_settings)

    def on_start(self):
        time.sleep(0.2)
        self.load_playlist(self.config['default_playlist'])

    def open_settings(self):
        """Open the settings dialog."""
        logging.info("Opening settings dialog.")
        self.settings_manager.show()

    def get_playlist_names(self):
        """Retrieve available playlist names and song counts from the predefined directory."""
        playlist_folder = self.config.get('root_playlist_folder', "playlists")
        
        # Check if the playlist folder exists
        if not os.path.exists(playlist_folder):
            logging.warning(f"Playlist folder does not exist: {playlist_folder}")
            return []

        playlists = []
        default_playlist_name = self.config.get('default_playlist', 'default')

        for f in os.listdir(playlist_folder):
            if f.endswith('.json'):
                playlist_path = os.path.join(playlist_folder, f)
                try:
                    with open(playlist_path, 'r') as file:
                        data = json.load(file)
                        name = data.get("playlist_name", os.path.splitext(f)[0])
                        playlist_image = data.get("playlist_large_image_key", None)
                        song_count = data.get("song_count", 0)
                        # Store both name and file path for later use
                        playlists.append((name, playlist_path, song_count, playlist_image))
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON in playlist file: {playlist_path}")
                except IOError as e:
                    logging.error(f"Error reading playlist file: {playlist_path}; {e}")

        if not playlists:
            logging.info("No playlists found in the folder.")
        
        # Move the default playlist to the top
        playlists = sorted(playlists, key=lambda x: x[0] == default_playlist_name, reverse=True)

        logging.info(f"Available playlists: {playlists}")
        return playlists
    
    def load_playlist_from_list(self, current, previous):
        if current:
            selected_playlist = current.text()
            playlist_folder = self.config.get('root_playlist_folder', "playlists")

            # Find the playlist path
            playlist_name = re.match(r'(.*) \(\d+ Songs\)', selected_playlist).group(1)
            playlist_file = f"{playlist_name}.json"
            playlist_path = os.path.join(playlist_folder, playlist_file)

            if os.path.exists(playlist_path):
                self.load_playlist(playlist_name)
            else:
                logging.error(f"Error loading playlist: Playlist file not found: {playlist_path}")

    def load_playlist(self, playlist_name):
        logging.info(f"Loading playlist: {playlist_name}")

        try:
            playlist_name, self.songs, playlist_image = self.playlist_manager.load_playlist(playlist_name)
        except FileNotFoundError as e:
            logging.error(f"Error loading playlist: {e}")
            return
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return

        self.current_playlist = playlist_name
        self.current_playlist_image = playlist_image
        self.playlist_name_var = playlist_name

        self.song_list.clear()
        if self.songs:
            for song in self.songs:
                self.song_list.addItem(f"{song['artist']} - {song['title']}")
            if mixer.music.get_busy():
                logging.info("Current song is playing, not updating title and song info.")
            else:
                self.setWindowTitle(f"Iota Player • {playlist_name}")
                self.song_index = 0
                self.current_song = self.songs[self.song_index]
                self.update_song_info()
                logging.info(f"Playlist loaded with {len(self.songs)} songs.")
        else:
            self.current_song = None
            self.update_song_info()
            logging.info("Playlist is empty.")
            
        # Reset shuffle state
        self.shuffled_songs = []
        self.shuffled_index = 0
        self.toggle_shuffle()  # If shuffle was enabled, reapply shuffle

        if not mixer.music.get_busy():
            self.toggle_shuffle()
            
    def load_playlist_dialog(self):
        playlist_path, _ = QFileDialog.getOpenFileName(self, "Load Playlist", self.config['root_playlist_folder'], "Playlist Files (*.json)")
        if playlist_path:
            playlist_name = os.path.splitext(os.path.basename(playlist_path))[0]
            logging.info(f"Loading playlist from dialog: {playlist_name}")
            self.load_playlist(playlist_name)
        else:
            logging.warning("No playlist file selected.")
            pass
        
    def reload_playlists(self):
        """Reload the list of playlists from the configuration folder."""
        logging.info("Reloading playlists.")
        
        # Update the list of playlists
        playlists = self.get_playlist_names()
        
        # Clear and update the playlist list widget
        self.playlist_list.clear()
        for name, _, count, _ in playlists:
            self.playlist_list.addItem(f"{name} ({count} Songs)")

        logging.info("Playlists reloaded.")
        
    def delete_playlist(self):
        """Delete the currently selected playlist."""
        current_item = self.playlist_list.currentItem()
        if not current_item:
            logging.warning("No playlist selected for deletion.")
            return

        selected_playlist = current_item.text()
        playlist_name = re.match(r'(.*) \(\d+ Songs\)', selected_playlist).group(1)
        playlist_file = f"{playlist_name}.json"
        playlist_folder = self.config.get('root_playlist_folder', "playlists")
        playlist_path = os.path.join(playlist_folder, playlist_file)

        reply = QMessageBox.question(self, 'Delete Playlist',
                                    f"Are you sure you want to delete the playlist '{playlist_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if os.path.exists(playlist_path):
                try:
                    os.remove(playlist_path)
                    logging.info(f"Deleted playlist: {playlist_name}")
                    
                    # Remove the playlist from the UI
                    self.playlist_list.takeItem(self.playlist_list.currentRow())
                    self.playlists = self.get_playlist_names()
                    logging.info(f"Updated playlist list after deletion.")
                    
                except Exception as e:
                    logging.error(f"Error deleting playlist: {e}")
            else:
                logging.error(f"Playlist file not found: {playlist_path}")
                
    def check_discord_connection(self):
        is_connected = self.discord_integration.is_connected()
        self.update_discord_status(is_connected)

    def update_discord_status(self, is_connected):
        status = "Connected" if is_connected else "Disconnected"
        self.discord_status_label.setText(f"Discord Status: {status}")
        #logger.info(f"Discord connection status updated to: {status}")

    def adjust_volume(self, value):
        """Adjusts the volume of the music player."""
        volume = value / 100.0
        mixer.music.set_volume(volume)
        #logging.info(f"Volume set to: {volume}")        

    def keyPressEvent(self, event):
        """Handle key press events within the PyQt5 application."""
        if event.key() == Qt.Key_Delete:
            self.delete_playlist()
        super().keyPressEvent(event)

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.media_play_pause:
                self.send_playpause_key()
            elif key == keyboard.Key.media_next:
                self.send_nexttrack_key()
            elif key == keyboard.Key.media_previous:
                self.send_prevtrack_key()
        except AttributeError:
            logging.warning(f"Unhandled key press: {key}")

    def send_prevtrack_key(self):
        logging.info("Sending previous track key")
        self.prev_song()

    def send_nexttrack_key(self):
        logging.info("Sending next track key")
        self.next_song()

    def send_playpause_key(self):
        logging.info("Sending play/pause key")
        
        if self.is_paused:
            logging.info("Music is paused, attempting to resume...")
            self.resume_music()  # Should resume music
        elif mixer.music.get_busy():
            logging.info("Music is playing, attempting to pause...")
            self.pause_music()  # Should pause music
        else:
            logging.info("No music is playing, attempting to start...")
            self.toggle_play()  # Start playing music

    def play_selected_song(self, item):
        """Play the song selected from the song list."""
        if item:
            song_text = item.text()
            song_info = song_text.split(" - ")
            if len(song_info) == 2:
                artist, title = song_info
                # Find the full song info based on artist and title
                for song in self.songs:
                    if song['artist'] == artist and song['title'] == title:
                        if self.current_song != song:
                            self.current_song = song
                            logging.info(f"Selected song: {self.current_song['artist']} - {self.current_song['title']}")
                            self.play_music()
                        return
                logging.warning(f"Song not found in playlist: {artist} - {title}")
            else:
                logging.warning(f"Invalid song format selected: {song_text}")

    def play_music(self):
        logging.info(f"Playing music: {self.current_song}")
        if self.current_song:
            mixer.music.load(self.current_song['path'])
            mixer.music.play()
            self.has_started = True
            self.is_playing = True
            self.is_paused = False
            self.update_song_info()  # Handle Discord presence

            # Toggle Play button to Stop
            self.toggle_play_button.setText("Stop")
            
            logging.info(f"Music started: {self.current_song['title']}")
        else:
            #logging.warning("No song selected for playback.")
            pass

    def stop_music(self):
        if mixer.music.get_busy():
            mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.has_started = False
            self.update_song_info()  # Handle Discord presence

            # Toggle Stop button to Play
            self.toggle_play_button.setText("Play")
            
            logging.info("Music stopped.")
        else:
            #logging.warning("Music is not currently playing.")
            pass

    def toggle_play(self):
        if self.is_playing:
            self.stop_music()
        else:
            self.play_music()

    def pause_music(self):
        logging.info("Pausing music.")
        if mixer.music.get_busy() and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True
            self.update_song_info()  # Handle Discord presence

            # Toggle Pause button to Resume
            self.toggle_pause_button.setText("Resume")
            
            logging.info("Music paused.")
        else:
            #logging.warning("Music is either not playing or already paused.")
            pass

    def resume_music(self):
        logging.info("Resuming music.")
        if self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
            self.update_song_info()  # Handle Discord presence

            # Toggle Resume button to Pause
            self.toggle_pause_button.setText("Pause")
            
            logging.info(f"Music resumed: {self.current_song['title']}")
        else:
            #logging.warning("Music is already playing or not paused.")
            pass

    def toggle_pause(self):
        if self.is_paused:
            self.resume_music()
        else:
            self.pause_music()
        
    def next_song(self):
        #logging.info("Skipping to next song.")
        if not self.songs:
            #logging.warning("No songs available in the current playlist.")
            return

        if self.is_shuffling and self.current_playlist:
            shuffled_songs = self.playlist_manager.shuffled_songs[self.current_playlist]
            if self.shuffled_index >= len(shuffled_songs):
                self.shuffled_index = 0
            self.current_song = shuffled_songs[self.shuffled_index]
            self.shuffled_index += 1
        else:
            self.song_index = (self.song_index + 1) % len(self.songs)
            self.current_song = self.songs[self.song_index]
        self.play_music()

    def prev_song(self):
        #logging.info("Skipping to previous song.")
        if not self.songs:
            #logging.warning("No songs available in the current playlist.")
            return

        if self.is_shuffling and self.current_playlist:
            shuffled_songs = self.playlist_manager.shuffled_songs[self.current_playlist]
            if self.shuffled_index <= 0:
                self.shuffled_index = len(shuffled_songs) - 1
            else:
                self.shuffled_index -= 1
            self.current_song = shuffled_songs[self.shuffled_index]
        else:
            self.song_index = (self.song_index - 1) % len(self.songs)
            self.current_song = self.songs[self.song_index]
        self.play_music()

    def highlight_current_song(self):
        """Highlight the currently playing song in the song list."""
        if self.is_shuffling:
            current_song_title = f"{self.current_song['artist']} - {self.current_song['title']}"
            items = [self.song_list.item(i).text() for i in range(self.song_list.count())]
            try:
                index = items.index(current_song_title)
                self.song_list.setCurrentRow(index)
            except ValueError:
                logging.warning(f"Current song {current_song_title} not found in song list.")
        else:
            if self.song_index is not None:
                self.song_list.setCurrentRow(self.song_index)

    def update_song_info(self):
        if self.current_song:
            self.song_info_var = f"{self.current_song['artist']} - {self.current_song['title']}"
            self.song_info_label.setText(self.song_info_var)
        else:
            self.song_info_var = "Nothing is playing"
            self.song_info_label.setText(self.song_info_var)
        
        # Temporarily disconnect the signal while updating the selection
        self.song_list.currentItemChanged.disconnect(self.play_selected_song)

        # Update UI elements
        self.highlight_current_song()

        # Reconnect the signal
        self.song_list.currentItemChanged.connect(self.play_selected_song)
        
        self.setWindowTitle(f"Iota Player • {self.current_playlist} • {self.song_info_var}")
        
        # Determine loop status for Discord presence
        small_image_key = "play"  # Default to play icon
        small_image_text = "Playing"  # Default to playing text
        
        if self.is_looping == "Song":
            small_image_key = "repeat-one"  # Small image key for song repeat
            small_image_text = "Looping Song"  # Text for song repeat
        elif self.is_looping == "Playlist":
            small_image_key = "repeat"  # Small image key for playlist repeat
            small_image_text = "Looping Playlist"  # Text for playlist repeat
            
        # Update Discord presence
        if self.config['connect_to_discord']:  # Check if Discord connection is enabled
            image_text = f"{self.current_playlist}"
            if self.is_playing:  # Check if something is playing
                if self.is_paused:  # Check if it is paused
                    self.discord_integration.update_presence(
                        f"{self.current_song['title']}", # Title
                        f"{self.current_song['artist']}", # Artist
                        image_text, # Large image text
                        "pause", # Small image key
                        "Paused", # Small image text
                        0, # Youtube ID for button
                        self.current_playlist_image if self.current_playlist else None, # Playlist image
                        None, # Duration
                    )
                else:  # Playing and not paused
                    title = f"{self.current_song['title']}" if self.current_song else "No song playing"
                    artist = f"{self.current_song['artist']}" if self.current_song else "No artist"
                    song_duration = self.get_song_length(self.current_song['path']) if self.current_song else 0
                    self.discord_integration.update_presence(
                        title, # Title
                        artist, # Artist
                        image_text, # Large image text
                        small_image_key, # Small image key
                        small_image_text,  # Small image text
                        self.current_song.get('youtube_id') if self.current_song else None, # Youtube ID for button
                        self.current_playlist_image if self.current_playlist else None, # Playlist image
                        song_duration, # Duration
                    )
            else:  # No song is playing
                self.discord_integration.update_presence(
                    "Nothing is playing", # Title
                    "Literally nothing.", # Artist
                    "No playlist", # Large image text
                    "stop", # Small image key
                    "Stopped", # Small image text
                    None,  # Youtube ID for button
                    None, # Playlist image
                    None # Duration
                )

    def update_progress(self):
        if mixer.music.get_busy():
            elapsed_time = mixer.music.get_pos() // 1000
            total_time = self.get_song_length(self.current_song['path'])
            elapsed_str = self.format_time(elapsed_time)
            total_str = self.format_time(total_time)
            self.time_label.setText(f"{elapsed_str} / {total_str}")
            self.progress_bar.setValue(int((elapsed_time / total_time) * 100))
            self.setWindowTitle(f"Iota Player • {self.current_playlist} ({len(self.songs)} songs) • {self.song_info_var} • {elapsed_str} / {total_str}")

    def check_song_end(self):
        if self.has_started and not mixer.music.get_busy() and self.current_song:
            if not self.is_paused:
                #logging.info("Song ended.")
                self.handle_song_end()
            else:
                #logging.info("Song ended but is paused.")
                pass
                
    def toggle_loop(self):
        if self.is_looping == "Off":
            self.is_looping = "Song"
            self.loop_button.setText("Loop Song")
        elif self.is_looping == "Song":
            self.is_looping = "Playlist"
            self.loop_button.setText("Loop Playlist")
        elif self.is_looping == "Playlist":
            self.is_looping = "Off"
            self.loop_button.setText("Loop Off")
        #logging.info(f"Loop mode set to: {self.is_looping}")

    def shuffle_songs(self):
        if self.current_playlist:
            self.playlist_manager.shuffle_songs(self.current_playlist)
            self.is_shuffling = True
            self.shuffled_index = 0
            logging.info("Songs shuffled.")

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        self.shuffle_button.setText("Shuffle On" if self.is_shuffling else "Shuffle Off")
        if self.is_shuffling:
            self.shuffle_songs()
        logging.info(f"Shuffle mode set to: {'ON' if self.is_shuffling else 'OFF'}")

    def get_song_length(self, song_path):
        audio = MP3(song_path)
        return int(audio.info.length)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

    def handle_song_end(self):
        #logging.info("Handling song end.")
        if self.is_looping == "Song":
            #logging.info(f"Looping current song: {self.current_song}")
            self.play_music()
        elif self.is_looping == "Playlist":
            #logging.info("Looping playlist.")
            self.next_song()
        else:
            #logging.info("No looping is set.")
            self.stop_music()

    def open_youtube(self):
        """Open the YouTube video for the current song."""
        if self.current_song and 'youtube_id' in self.current_song:
            youtube_url = f"https://www.youtube.com/watch?v={self.current_song['youtube_id']}"
            webbrowser.open(youtube_url)
            logging.info(f"Opened YouTube video: {youtube_url}")
            
    def open_playlist_maker(self):
        logging.info("Opening Playlist Maker")
        self.playlist_maker_window = PlaylistMaker(self.icon_path)
        self.playlist_maker_window.show()
