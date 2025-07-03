# =============
# Music Player Core Logic
#
# This module implements the main player window, playback controls, UI updates,
# and state management for IotaPlayer. It handles song loading, playlist navigation,
# cover art display, Discord integration, and MPRIS metadata updates.
# =============
import os
import webbrowser
import threading
import logging
import json
import re
import time
from PyQt5.QtWidgets import (
    QDialog,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QListWidget,
    QFileDialog,
    QLabel,
    QSlider,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QInputDialog,
)
from utils import hex_to_rgba
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QUrl, QByteArray
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from pynput import keyboard
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from core.discordIntegration import DiscordIntegration, PresenceUpdateData
from core.playlistMaker import PlaylistMaker, PlaylistManager
from core.settingManager import SettingsDialog
from core.imageCache import CoverArtCache
from core.google import (
    get_authenticated_service,
    create_youtube_playlist,
    add_videos_to_youtube_playlist,
)
from config import discord_cdn_images
from fuzzywuzzy import process


class YouTubeUploadThread(QThread):
    progress = pyqtSignal(str)  # Signal to report progress steps
    finished_signal = pyqtSignal(str)  # Signal when done (success message)
    error = pyqtSignal(str)  # Signal on error

    def __init__(self, playlist_title, video_ids):
        super().__init__()
        self.playlist_title = playlist_title
        self.video_ids = video_ids

    def run(self):
        try:
            self.progress.emit("Authenticating with Google...")
            service = get_authenticated_service()  # From core.google
            if not service:
                self.error.emit(
                    "Failed to authenticate with Google. Check console/logs."
                )
                return

            self.progress.emit(f"Creating YouTube playlist '{self.playlist_title}'...")
            new_playlist_id = create_youtube_playlist(
                service, self.playlist_title, privacy_status="private"
            )  # Or 'public'/'unlisted'
            if not new_playlist_id:
                self.error.emit("Failed to create YouTube playlist.")
                return

            self.progress.emit(f"Adding {len(self.video_ids)} videos to playlist...")
            added_count, errors = add_videos_to_youtube_playlist(
                service, new_playlist_id, self.video_ids
            )

            result_message = f"Successfully created playlist '{self.playlist_title}' (ID: {new_playlist_id}).\n"
            result_message += (
                f"Added {added_count} out of {len(self.video_ids)} videos."
            )
            if errors:
                result_message += (
                    f"\n\nErrors occurred for {len(errors)} videos:\n"
                    + "\n".join(errors[:5])
                )  # Show first 5 errors
                if len(errors) > 5:
                    result_message += "\n..."

            self.finished_signal.emit(result_message)

        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {str(e)}")


class MusicPlayer(QMainWindow):
    def __init__(self, settings, icon_path, config_path, theme, normal):
        super().__init__()
        self.icon_path = icon_path
        self.clr_theme = theme
        self.clr_nrm = normal
        self.config_path = config_path
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Iota Player • Music Player")
        self.setMinimumSize(1000, 600)

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logging.info(
                "Config file not found or invalid. Creating a new one with default settings."
            )
            self.config = settings
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4)
            except IOError as e:
                logging.error(f"Error writing to config file: {e}")
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
            except IOError as e:
                logging.error(f"Error reading from config file: {e}")

        playlist_folder = self.config.get("root_playlist_folder", "playlists")
        if not os.path.exists(playlist_folder):
            os.makedirs(playlist_folder)
            logging.info(f"Created playlist folder: {playlist_folder}")

        self.initUI()
        self.set_stylesheet(theme, normal)
        self.cover_cache = CoverArtCache()
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.start()
        self.playlist_manager = PlaylistManager()
        self.discord_integration = DiscordIntegration()
        self.settings_manager = SettingsDialog(settings, icon_path, config_path)
        self.discord_integration.connection_status_changed.connect(
            self.update_discord_status
        )
        self.current_playlist_image = None
        self.current_song = None
        self.time_played = 0
        self.start_time = 0
        self.pause_start_time = 0
        self.total_paused_time = 0
        self.song_duration = 0
        self.songs = []
        self.song_index = 0
        self.is_looping = "Off"
        logging.info(f"Initialized Iota Player with is_looping = {self.is_looping}")
        self.is_playing = False
        logging.info(f"Initialized Iota Player with is_playing = {self.is_playing}")
        self.is_shuffling = False
        self.shuffled_index = 0
        logging.info(
            f"Initialized Iota Player with is_shuffling = {self.is_shuffling}; shuffled_index = {self.shuffled_index}"
        )

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

        self.media_player = QMediaPlayer()
        self.on_start()
        self.has_started = False
        self.is_paused = False
        
        self.media_player.positionChanged.connect(self.update_progress)
        #self.media_player.durationChanged.connect(self.update_duration)
        #self.media_player.stateChanged.connect(self.handle_state_change)
        
        self.volume_update_timer = QTimer()
        self.volume_update_timer.timeout.connect(self.update_volume_slider)
        self.volume_update_timer.start(1000)

    def set_stylesheet(self, theme, normal):
        if theme == "dark":
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
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Top Layout: Left Frame (Playlist), Middle Frame (Song List), and Right Frame (Song Info)
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
        self.playlist_combine_button = QPushButton("Combine Playlists")
        self.playlist_maker_button = QPushButton("Manage")
        self.playlist_maker_button.setFixedWidth(70)
        self.left_frame_scnd_layout.addWidget(self.playlist_list_label)
        self.left_frame_scnd_layout.addWidget(self.playlist_combine_button)
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
        self.upload_youtube_button = QPushButton("Upload to YouTube")

        self.three_button_layout.addWidget(self.load_button)
        self.three_button_layout.addWidget(self.reload_button)
        self.three_button_layout.addWidget(self.delete_button)
        self.two_button_layout.addWidget(self.shuffle_button)
        self.two_button_layout.addWidget(self.loop_button)
        self.one_button_layout.addWidget(self.youtube_button)
        self.one_button_layout.addWidget(self.upload_youtube_button)

        client_secret_path = self.config.get("google_client_secret_file", "")
        if not client_secret_path or not os.path.exists(client_secret_path):
            self.upload_youtube_button.setEnabled(False)
            self.upload_youtube_button.setToolTip("Set a valid Google client secret file in Settings to enable YouTube upload.")
        else:
            self.upload_youtube_button.setEnabled(True)
            self.upload_youtube_button.setToolTip("")

        # left frame sliders
        self.sliders_layout = QVBoxLayout()
        self.left_frame_layout.addLayout(self.sliders_layout)

        self.time_label = QLabel("00:00 / 00:00")
        self.sliders_layout.addWidget(self.time_label)

        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.sliders_layout.addWidget(self.progress_bar)

        self.get_volume = self.config.get("volume_percentage", 100)
        self.volume_label = QLabel(f"Volume: {self.get_volume}%")
        self.sliders_layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)

        self.volume_slider.setValue(self.get_volume)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setSingleStep(1)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        self.sliders_layout.addWidget(self.volume_slider)

        # Middle Frame Layout (Song List)
        self.middle_frame = QWidget()
        self.middle_frame_layout = QVBoxLayout()
        self.middle_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_frame_layout.setSpacing(10)
        self.middle_frame.setLayout(self.middle_frame_layout)
        self.top_layout.addWidget(self.middle_frame)

        self.middle_frame_scnd_layout = QHBoxLayout()
        self.search_layout = QHBoxLayout()
        self.middle_frame_layout.addLayout(self.middle_frame_scnd_layout)
        self.middle_frame_layout.addLayout(self.search_layout)

        # Song List, Settings, and Search Layout
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.search_songs)

        self.search_type_dropdown = QComboBox()
        self.search_type_dropdown.addItems(["Artist & Title", "Genre", "Album"])

        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_type_dropdown)

        self.song_list_label = QLabel("Song List:")
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedWidth(70)
        self.middle_frame_scnd_layout.addWidget(self.song_list_label)
        self.middle_frame_scnd_layout.addWidget(self.settings_button)
        self.song_list = QListWidget()
        self.song_list.currentItemChanged.connect(self.play_selected_song)
        self.middle_frame_layout.addWidget(self.song_list)

        # Right Frame Layout (Song Info)
        self.right_frame = QWidget()
        self.right_frame_layout = QVBoxLayout()
        self.right_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.right_frame_layout.setSpacing(10)
        self.right_frame.setLayout(self.right_frame_layout)
        self.right_frame.setFixedWidth(270)

        # Apply the background color and border
        if self.clr_theme == "dark":
            self.right_frame.setStyleSheet(
                f"background-color: {hex_to_rgba(self.clr_nrm, 0.1)}; border: 1px solid #3f4042; border-radius: 5px;"
            )
        else:
            self.right_frame.setStyleSheet(
                f"background-color: {hex_to_rgba(self.clr_nrm, 0.1)}; border: 1px solid #dadce0; border-radius: 5px;"
            )

        self.top_layout.addWidget(
            self.right_frame, alignment=Qt.AlignTop | Qt.AlignRight
        )

        # Song Info (Song picture, title, author, etc.)
        self.song_picture = QLabel()
        self.song_picture.setContentsMargins(0, 9, 0, 0)
        self.song_picture.setPixmap(QPixmap("").scaled(250, 250, Qt.KeepAspectRatio))
        self.song_picture.setStyleSheet("border: none; background-color: none;")

        self.right_frame_layout.addWidget(self.song_picture, alignment=Qt.AlignCenter)

        # Style labels
        if self.clr_theme == "dark":
            label_stylesheet = "border: none; background: none; color: #FFFFFF;"
        else:
            label_stylesheet = "border: none; background: none; color: #000000;"

        self.song_title_label = QLabel("Title:")
        self.song_title_label.setAlignment(Qt.AlignLeft)
        self.song_title_label.setContentsMargins(10, 0, 0, 0)
        self.song_title_label.setStyleSheet(label_stylesheet)
        self.right_frame_layout.addWidget(self.song_title_label)

        self.song_author_label = QLabel("Author:")
        self.song_author_label.setAlignment(Qt.AlignLeft)
        self.song_author_label.setContentsMargins(10, 0, 0, 0)
        self.song_author_label.setStyleSheet(label_stylesheet)
        self.right_frame_layout.addWidget(self.song_author_label)

        self.song_album_label = QLabel("Album:")
        self.song_album_label.setAlignment(Qt.AlignLeft)
        self.song_album_label.setContentsMargins(10, 0, 0, 0)
        self.song_album_label.setStyleSheet(label_stylesheet)
        self.right_frame_layout.addWidget(self.song_album_label)

        self.song_genre_label = QLabel("Genre:")
        self.song_genre_label.setAlignment(Qt.AlignLeft)
        self.song_genre_label.setContentsMargins(10, 0, 0, 10)
        self.song_genre_label.setStyleSheet(label_stylesheet)
        self.right_frame_layout.addWidget(self.song_genre_label)

        # Bottom Layout: Music Control, Progress, Volume
        self.bottom_layout = QVBoxLayout()
        self.main_layout.addLayout(self.bottom_layout)

        # Music Control Buttons
        self.music_control_layout = QHBoxLayout()
        self.music_control_layout.setContentsMargins(0, 0, 0, 0)
        self.music_control_layout.setSpacing(10)

        # Add a left spacer
        self.left_spacer = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.music_control_layout.addItem(self.left_spacer)

        # Create buttons
        self.prev_button = QPushButton("Previous")
        self.toggle_pause_button = QPushButton("Pause")  # Toggle Pause/Resume
        self.toggle_play_button = QPushButton("Play")  # Toggle Play/Stop
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
        self.right_spacer = QSpacerItem(
            20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.music_control_layout.addItem(self.right_spacer)

        # Add layout to the bottom layout or your main layout
        self.bottom_layout.addLayout(self.music_control_layout)

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
        self.playlist_combine_button.clicked.connect(self.combine_playlists_mp)
        self.playlist_maker_button.clicked.connect(self.open_playlist_maker)
        self.settings_button.clicked.connect(self.open_settings)
        self.upload_youtube_button.clicked.connect(self.initiate_youtube_upload_dialog)
        self.progress_bar.sliderReleased.connect(self.seek_in_song)
        """
        self.next_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.playlist_combine_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.playlist_maker_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.settings_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.youtube_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.reload_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.delete_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.upload_youtube_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.toggle_play_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.toggle_pause_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.prev_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.song_album_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.song_genre_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.song_author_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.song_title_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.settings_button.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.song_list_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.search_bar.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.volume_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        self.time_label.setFont(QFont(self.config.get("font_name", "Noto Sans"), 10, QFont.Normal))
        """

    def seek_in_song(self):
        """Seek to the position in the song based on the slider value."""
        if self.media_player.duration() > 0:
            # Get the slider value (0-100)
            slider_value = self.progress_bar.value()
            # Calculate the position in milliseconds
            new_position = int((slider_value / 100) * self.media_player.duration())
            self.media_player.setPosition(new_position)
            self.update_song_info()

    def update_youtube_button_state(self):
        client_secret_path = self.config.get("google_client_secret_file", "")
        if not client_secret_path or not os.path.exists(client_secret_path):
            self.upload_youtube_button.setEnabled(False)
            self.upload_youtube_button.setToolTip("Set a valid Google client secret file in Settings to enable YouTube upload.")
        else:
            self.upload_youtube_button.setEnabled(True)
            self.upload_youtube_button.setToolTip("")

    def initiate_youtube_upload_dialog(self):
        client_secret_path = self.config.get("google_client_secret_file", "")
        if not client_secret_path or not os.path.exists(client_secret_path):
            QMessageBox.warning(
                self,
                "Missing Google Client Secret",
                "Google client secret file is missing or invalid. Please set it in Settings before uploading to YouTube."
            )
            return

        playlists_dir = self.config.get("root_playlist_folder", "playlists")
        if not os.path.exists(playlists_dir):
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"Playlist directory not found: {playlists_dir}",
            )
            return

        available_playlists = [
            f for f in os.listdir(playlists_dir) if f.endswith(".json")
        ]
        if not available_playlists:
            QMessageBox.information(
                self, "No Playlists", "No local playlists found to upload."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Select a Playlist")
        dialog.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout(dialog)
        list_widget = QListWidget(dialog)
        list_widget.addItems([os.path.splitext(p)[0] for p in available_playlists])
        layout.addWidget(list_widget)

        button_box = QHBoxLayout()
        layout.addLayout(button_box)

        select_button = QPushButton("Select", dialog)
        cancel_button = QPushButton("Cancel", dialog)
        button_box.addWidget(select_button)
        button_box.addWidget(cancel_button)

        def on_select():
            selected_item = list_widget.currentItem()
            if selected_item:
                selected_playlist_name = os.path.splitext(selected_item.text())[
                    0
                ]  # Assumes list shows "name.json"
                # --- Start processing the selected playlist ---
                dialog.accept()  # Close selection dialog
                self.process_playlist_for_upload(selected_playlist_name)
            else:
                QMessageBox.warning(
                    dialog, "Selection Error", "Please select a playlist."
                )

        def on_cancel():
            dialog.reject()  # Just close the dialog

        select_button.clicked.connect(on_select)
        cancel_button.clicked.connect(on_cancel)

        dialog.exec_()

    def process_playlist_for_upload(self, playlist_name):
        playlist_path = os.path.join(
            self.config.get("root_playlist_folder", "playlists"),
            playlist_name + ".json",
        )
        logging.info(f"Processing playlist for YouTube upload: {playlist_path}")

        try:
            with open(playlist_path, "r", encoding="utf-8") as f:
                playlist_data = json.load(f)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load playlist file '{playlist_path}': {e}"
            )
            logging.error(f"Failed to load playlist file '{playlist_path}': {e}")
            return

        # --- Extract and Validate YouTube IDs ---
        video_ids = []
        missing_ids_info = []
        songs_in_playlist = playlist_data.get("songs", [])

        if not songs_in_playlist:
            QMessageBox.warning(
                self, "Empty Playlist", "The selected playlist contains no songs."
            )
            return

        for song in songs_in_playlist:
            yt_id = song.get("youtube_id")
            if yt_id:
                video_ids.append(yt_id)
            else:
                missing_ids_info.append(
                    f"{song.get('artist', 'Unknown')} - {song.get('title', 'Unknown')}"
                )

        if not video_ids:
            QMessageBox.warning(
                self,
                "No YouTube IDs",
                "No songs with YouTube IDs found in this playlist.",
            )
            return

        if missing_ids_info:
            reply = QMessageBox.question(
                self,
                "Missing IDs",
                f"Warning: {len(missing_ids_info)} song(s) are missing YouTube IDs and will be skipped.\nProceed anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # --- Get YouTube Playlist Name ---
        local_playlist_title = playlist_data.get("playlist_name", playlist_name)
        youtube_playlist_title, ok = QInputDialog.getText(
            self,
            "YouTube Playlist Name",
            "Enter name for the new YouTube playlist:",
            text=local_playlist_title,
        )
        if not ok or not youtube_playlist_title.strip():
            QMessageBox.information(self, "Cancelled", "YouTube upload cancelled.")
            return
        youtube_playlist_title = (
            youtube_playlist_title.strip()
        )  # Ensure no leading/trailing whitespace

        # --- Start Background Thread ---
        # Disable the upload button to prevent multiple clicks
        self.upload_youtube_button.setEnabled(False)
        # Update status bar or label
        # self.statusBar().showMessage("Starting YouTube upload...")

        self.youtube_thread = YouTubeUploadThread(youtube_playlist_title, video_ids)
        # Connect signals from the thread to slots in MusicPlayer for feedback
        self.youtube_thread.progress.connect(self.update_youtube_progress)
        self.youtube_thread.finished_signal.connect(self.on_youtube_upload_finished)
        self.youtube_thread.error.connect(self.on_youtube_upload_error)
        self.youtube_thread.start()

    # --- Add slots to handle thread signals ---
    def update_youtube_progress(self, message):
        logging.info(f"YouTube Upload Progress: {message}")
        # Update a status label or progress bar
        #self.statusBar().showMessage(message)

    def on_youtube_upload_finished(self, result_message):
        logging.info(f"YouTube Upload Finished: {result_message}")
        QMessageBox.information(self, "Upload Complete", result_message)
        self.upload_youtube_button.setEnabled(True)  # Re-enable button
        # self.statusBar().clearMessage()

    def on_youtube_upload_error(self, error_message):
        logging.error(f"YouTube Upload Error: {error_message}")
        QMessageBox.critical(
            self,
            "Upload Error",
            f"An error occurred during the YouTube upload:\n{error_message}",
        )
        self.upload_youtube_button.setEnabled(True)  # Re-enable button
        #self.statusBar().showMessage("Upload failed.")

    def display_song_text(self, song):
        """Return a display string for a song, avoiding duplicate artist in title."""
        artist = str(song.get('artist', '')).strip()
        title = str(song.get('title', '')).strip()
        # Remove punctuation and lowercase for comparison
        def normalize(s):
            return re.sub(r'[^\w]', '', s).lower()
        if artist and normalize(title).startswith(normalize(artist)):
            return title
        return f"{artist} - {title}" if artist else title

    def search_songs(self, query):
        search_type = self.search_type_dropdown.currentText()
        if not query:
            self.song_list.clear()
            for song in self.songs:
                self.song_list.addItem(self.display_song_text(song))
            return

        results = []
        for song in self.songs:
            if search_type == "Artist & Title":
                song_info = f"{song['artist']} - {song['title']}"
            elif search_type == "Genre":
                song_info = song["genre"]
            elif search_type == "Album":
                song_info = song["album"]
            else:
                song_info = f"{song['artist']} - {song['title']} - {song['album']} - {song['genre']}"

            match = process.extractOne(query, [song_info])
            if match and match[1] > 70:
                results.append(song)

        self.song_list.clear()
        for song in results:
            self.song_list.addItem(self.display_song_text(song))

    def combine_playlists_mp(self):
        self.playlist_manager.combine_playlists()
        time.sleep(1)
        self.reload_playlists()

    def on_start(self):
        time.sleep(0.2)
        self.load_playlist(self.config["default_playlist"])

    def open_settings(self):
        """Open the settings dialog."""
        logging.info("Opening settings dialog.")
        self.settings_manager.show()

    def get_playlist_names(self):
        """Retrieve available playlist names and song counts from the predefined directory, plus Unsorted Music if set."""
        playlist_folder = self.config.get("root_playlist_folder", "playlists")
        unsorted_folder = self.config.get("unsorted_music_folder", "")

        playlists = []
        default_playlist_name = self.config.get("default_playlist", "default")

        # Add Unsorted Music as a virtual playlist if set and exists
        if unsorted_folder and os.path.exists(unsorted_folder):
            # Count audio files
            count = 0
            for root, _, files in os.walk(unsorted_folder):
                count += len([f for f in files if f.lower().endswith((".mp3", ".flac", ".ogg", ".wav", ".m4a"))])
            playlists.append(("Unsorted Music", None, count, None))

        # ...existing code for loading .json playlists...
        for f in os.listdir(playlist_folder):
            if f.endswith(".json"):
                playlist_path = os.path.join(playlist_folder, f)
                try:
                    with open(playlist_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        name = data.get("playlist_name", os.path.splitext(f)[0])
                        playlist_image = data.get("playlist_large_image_key", None)
                        song_count = data.get("song_count", 0)
                        playlists.append((name, playlist_path, song_count, playlist_image))
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON in playlist file: {playlist_path}")
                except IOError as e:
                    logging.error(f"Error reading playlist file: {playlist_path}; {e}")

        if not playlists:
            logging.info("No playlists found in the folder.")

        # Move the default playlist to the top (after Unsorted Music)
        playlists = sorted(
            playlists, key=lambda x: x[0] == default_playlist_name, reverse=True
        )

        logging.info(f"Available playlists: {playlists}")
        return playlists

    def load_playlist_from_list(self, current, previous):
        if current:
            selected_playlist = current.text()
            if selected_playlist.startswith("Unsorted Music"):
                self.load_unsorted_music()
                return
            # ...existing code...
            playlist_folder = self.config.get("root_playlist_folder", "playlists")
            playlist_name = re.match(r"(.*) \\(\d+ Songs\\)", selected_playlist).group(1)
            playlist_file = f"{playlist_name}.json"
            playlist_path = os.path.join(playlist_folder, playlist_file)
            if os.path.exists(playlist_path):
                self.load_playlist(playlist_name)
            else:
                logging.error(f"Error loading playlist: Playlist file not found: {playlist_path}")

    def load_unsorted_music(self):
        """Scan the unsorted music folder and build a song list on the fly."""
        unsorted_folder = self.config.get("unsorted_music_folder", "")
        if not unsorted_folder or not os.path.exists(unsorted_folder):
            QMessageBox.warning(self, "Unsorted Music", "Unsorted music folder is not set or does not exist.")
            return
        songs = []
        for root, _, files in os.walk(unsorted_folder):
            for f in files:
                if f.lower().endswith((".mp3", ".flac", ".ogg", ".wav", ".m4a")):
                    path = os.path.join(root, f)
                    # Try to extract metadata
                    try:
                        audio = MP3(path)
                        title = audio.get("TIT2", os.path.splitext(f)[0])
                        artist = audio.get("TPE1", "Unknown Artist")
                        album = audio.get("TALB", "Unknown Album")
                        genre = audio.get("TCON", "Unknown Genre")
                        song = {
                            "title": str(title),
                            "artist": str(artist),
                            "album": str(album),
                            "genre": str(genre),
                            "path": path,
                            "picture_path": "",
                            "picture_link": "",
                        }
                    except Exception:
                        song = {
                            "title": os.path.splitext(f)[0],
                            "artist": "Unknown Artist",
                            "album": "Unknown Album",
                            "genre": "Unknown Genre",
                            "path": path,
                            "picture_path": "",
                            "picture_link": "",
                        }
                    songs.append(song)
        self.current_playlist = "Unsorted Music"
        self.current_playlist_image = None
        self.playlist_name_var = "Unsorted Music"
        self.songs = songs
        self.song_list.clear()
        for song in self.songs:
            self.song_list.addItem(self.display_song_text(song))
        if self.songs:
            self.song_index = 0
            self.current_song = self.songs[self.song_index]
            self.update_song_info()
        else:
            self.current_song = None
            self.update_song_info()
        self.shuffled_songs = []
        self.shuffled_index = 0
        self.is_shuffling = False
        self.shuffle_button.setText("Shuffle Off")
        logging.info(f"Loaded Unsorted Music with {len(self.songs)} songs.")

    def load_playlist(self, playlist_name):
        logging.info(f"Loading playlist: {playlist_name}")

        try:
            playlist_name, self.songs, playlist_image = (
                self.playlist_manager.load_playlist(playlist_name)
            )
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
                self.song_list.addItem(self.display_song_text(song))
            if self.media_player.state() == QMediaPlayer.PlayingState:
                logging.info(
                    "Current song is playing, not updating title and song info."
                )
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

    def load_playlist_dialog(self):
        playlist_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Playlist",
            self.config["root_playlist_folder"],
            "Playlist Files (*.json)",
        )
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
        playlist_name = re.match(r"(.*) \(\d+ Songs\)", selected_playlist).group(1)
        playlist_file = f"{playlist_name}.json"
        playlist_folder = self.config.get("root_playlist_folder", "playlists")
        playlist_path = os.path.join(playlist_folder, playlist_file)

        reply = QMessageBox.question(
            self,
            "Delete Playlist",
            f"Are you sure you want to delete the playlist '{playlist_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if os.path.exists(playlist_path):
                try:
                    os.remove(playlist_path)
                    logging.info(f"Deleted playlist: {playlist_name}")

                    # Remove the playlist from the UI
                    self.playlist_list.takeItem(self.playlist_list.currentRow())
                    self.playlists = self.get_playlist_names()
                    logging.info("Updated playlist list after deletion.")

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
        # logger.info(f"Discord connection status updated to: {status}")

    def adjust_volume(self, value):
        """Adjusts the volume of the music player."""
        volume = value / 100.
        self.media_player.setVolume(int(volume * 100))  # QMediaPlayer expects 0-100
        self.volume_label.setText(f"Volume: {value}%")
        # logging.info(f"Volume set to: {value}%")

    def update_volume_slider(self):
        """Updates the volume slider based on the current system volume."""
        current_volume = self.media_player.volume()
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(int(current_volume))
        self.volume_slider.blockSignals(False)
        self.volume_label.setText(f"Volume: {int(current_volume)}%")

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
        elif self.media_player.state() == QMediaPlayer.PlayingState:
            logging.info("Music is playing, attempting to pause...")
            self.pause_music()
        else:
            logging.info("No music is playing, attempting to start...")
            self.toggle_play()

    def play_selected_song(self, item):
        """Play the song selected from the song list."""
        if item:
            song_text = item.text()
            song_info = song_text.split(" - ")
            if len(song_info) == 2:
                artist, title = song_info
                # Find the full song info based on artist and title
                for song in self.songs:
                    if song["artist"] == artist and song["title"] == title:
                        if self.current_song != song:
                            self.current_song = song
                            logging.info(
                                f"Selected song: {self.current_song['artist']} - {self.current_song['title']}"
                            )
                            self.play_music()
                        return
                logging.warning(f"Song not found in playlist: {artist} - {title}")
            else:
                logging.warning(f"Invalid song format selected: {song_text}")

    def set_mpris_player_iface(self, mpris_iface):
        """Inject the MPRIS player interface for D-Bus updates."""
        self.mpris_player_iface = mpris_iface

    def play_music(self):
        logging.info(f"Playing music: {self.current_song}")
        if self.current_song:
            url = QUrl.fromLocalFile(self.current_song["path"])
            self.media_player.setMedia(QMediaContent(url))
            self.media_player.play()

            # Track the start time and reset time played
            self.start_time = time.time()  # Set the current time as the start time
            self.time_played = 0  # Reset time played when starting a new song
            self.song_duration = self.get_song_length(self.current_song["path"])
            self.has_started = True
            self.is_playing = True
            self.is_paused = False
            self.total_paused_time = 0
            self.update_song_info()  # Handle Discord presence

            # Toggle Play button to Stop
            self.toggle_play_button.setText("Stop")

            # --- MPRIS: Update metadata ---
            if hasattr(self, "mpris_player_iface") and self.mpris_player_iface:
                self.mpris_player_iface.update_metadata()

            logging.info(f"Music started: {self.current_song['title']}")
        else:
            # logging.warning("No song selected for playback.")
            pass

    def stop_music(self):
        try:
            self.media_player.stop()
            self.is_playing = False
            self.is_paused = False
            self.has_started = False
            self.update_song_info()
            self.toggle_play_button.setText("Play")
            logging.info("Music stopped.")
        except Exception as e:
            logging.error(f"Error in stop_music: {e}")

    def toggle_play(self):
        if self.is_playing:
            self.stop_music()
        else:
            self.play_music()

    def pause_music(self):
        logging.info("Pausing music.")
        if not self.is_paused:
            self.media_player.pause()
            self.is_paused = True

            self.time_played += time.time() - self.start_time

            self.update_song_info()  # Handle Discord presence

            # Toggle Pause button to Resume
            self.toggle_pause_button.setText("Resume")

            logging.info("Music paused.")
        else:
            # logging.warning("Music is either not playing or already paused.")
            pass

    def resume_music(self):
        logging.info("Resuming music.")
        if self.is_paused:
            self.media_player.play()
            self.is_paused = False

            # Add the paused duration to total_paused_time
            self.start_time = time.time()  # Restart the timer

            self.update_song_info()  # Handle Discord presence

            # Toggle Resume button to Pause
            self.toggle_pause_button.setText("Pause")

            logging.info(f"Music resumed: {self.current_song['title']}")
        else:
            # logging.warning("Music is already playing or not paused.")
            pass

    def toggle_pause(self):
        if self.is_paused:
            self.resume_music()
        else:
            self.pause_music()

    def next_song(self):
        # logging.info("Skipping to next song.")
        if not self.songs:
            # logging.warning("No songs available in the current playlist.")
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
        # --- MPRIS: Update metadata ---
        if hasattr(self, "mpris_player_iface") and self.mpris_player_iface:
            self.mpris_player_iface.update_metadata()

    def prev_song(self):
        # logging.info("Skipping to previous song.")
        if not self.songs:
            # logging.warning("No songs available in the current playlist.")
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
        # --- MPRIS: Update metadata ---
        if hasattr(self, "mpris_player_iface") and self.mpris_player_iface:
            self.mpris_player_iface.update_metadata()

    def highlight_current_song(self):
        """Highlight the currently playing song in the song list."""
        if self.is_shuffling:
            current_song_title = (
                f"{self.current_song['artist']} - {self.current_song['title']}"
            )
            items = [
                self.song_list.item(i).text() for i in range(self.song_list.count())
            ]
            try:
                index = items.index(current_song_title)
                self.song_list.setCurrentRow(index)
            except ValueError:
                logging.warning(
                    f"Current song {current_song_title} not found in song list."
                )
        else:
            if self.song_index is not None:
                self.song_list.setCurrentRow(self.song_index)

    def update_song_info(self):
        if self.current_song:
            self.song_info_var = self.display_song_text(self.current_song)
            self.update_right_frame_info()  # Update the right frame with the song info
        else:
            self.song_info_var = "Nothing is playing"
            self.clear_right_frame_info()  # Clear the right frame info

        # --- Avoid disconnecting/reconnecting signals; use a flag instead ---
        self._ignore_song_list_signal = True
        self.highlight_current_song()
        self._ignore_song_list_signal = False

        self.setWindowTitle(
            f"Iota Player • {self.current_playlist} • {self.song_info_var}"
        )

        # Determine loop status for Discord presence
        small_image_key = discord_cdn_images["play"]  # Default to play icon
        small_image_text = "Playing"  # Default to playing text

        if self.is_looping == "Song":
            small_image_key = discord_cdn_images[
                "repeat-one"
            ]  # Small image key for song repeat
            small_image_text = "Looping Song"  # Text for song repeat
        elif self.is_looping == "Playlist":
            small_image_key = discord_cdn_images[
                "repeat"
            ]  # Small image key for playlist repeat
            small_image_text = "Looping Playlist"  # Text for playlist repeat

        # Update Discord presence
        if self.config["connect_to_discord"]:  # Check if Discord connection is enabled
            # Compose system info string
            #sys_info = f"{platform.system()} {platform.release()} | Python {platform.python_version()}"
            if self.current_playlist == "Unsorted Music":
                image_text = "Unsorted Music"
                big_image = discord_cdn_images.get("default_image")
            else:
                image_text = self.current_song.get("album") or self.current_playlist
                if self.current_song.get("picture_link"):
                    big_image = self.current_song["picture_link"]
                else:
                    big_image = (
                        self.current_playlist_image if self.current_playlist else None
                    )

        if self.is_playing:
            current_position = self.media_player.position() // 1000
            if self.is_paused:
                update_data = PresenceUpdateData(
                    song_title=self.current_song['title'],
                    artist_name=self.current_song['artist'],
                    large_image_text=image_text,
                    small_image_key=discord_cdn_images["pause"],
                    small_image_text="Paused",
                    image_key=big_image,
                    song_duration=self.song_duration,
                    time_played=current_position
                )
            else:
                update_data = PresenceUpdateData(
                    song_title=self.current_song['title'],
                    artist_name=self.current_song['artist'],
                    large_image_text=image_text,
                    small_image_key=small_image_key,
                    small_image_text=small_image_text,
                    youtube_id=self.current_song.get("youtube_id"),
                    image_key=big_image,
                    song_duration=self.song_duration,
                    time_played=current_position
                )
            self.discord_integration.update_presence(update_data)
        else:
            update_data = PresenceUpdateData(
                song_title="Nothing is playing",
                artist_name="Literally nothing.",
                large_image_text="No playlist",
                small_image_key=discord_cdn_images["stop"],
                small_image_text="Stopped",
                image_key=None
            )
            self.discord_integration.update_presence(update_data)

    def get_embedded_cover(self, song_path):
        """Return QPixmap of embedded cover art if present, else None."""
        try:
            audio = MP3(song_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    cover_data = tag.data
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(cover_data))
                    return pixmap
        except Exception as e:
            logging.warning(f"No embedded cover found or error reading cover: {e}")
        return None

    def truncate_text(self, text, max_length=42):
        return text if len(text) <= max_length else text[:max_length - 3] + "..."

    def update_right_frame_info(self):
        """Update the right frame with the current song's information."""
        if self.current_song:
            # Try cached/processed cover first
            cover_pixmap = self.cover_cache.get_cover(self.current_song["path"], size=250)
            if cover_pixmap and not cover_pixmap.isNull():
                self.song_picture.setPixmap(cover_pixmap)
            else:
                # Fallback to picture_path
                picture_path = self.current_song.get("picture_path", "default.png")
                if os.path.exists(picture_path):
                    self.song_picture.setPixmap(
                        QPixmap(picture_path).scaled(250, 250, Qt.KeepAspectRatio)
                    )
                else:
                    self.song_picture.setPixmap(
                        QPixmap("default.png").scaled(250, 250, Qt.KeepAspectRatio)
                    )

            # Update the labels with song information
            self.song_title_label.setText(
                "Title: " + self.truncate_text(self.current_song.get("title", "Unknown Title"))
            )
            self.song_author_label.setText(
                "Author: " + self.truncate_text(self.current_song.get("artist", "Unknown Artist"))
            )
            self.song_album_label.setText(
                "Album: " + self.truncate_text(self.current_song.get("album", "Unknown Album"))
            )
            self.song_genre_label.setText(
                "Genre: " + self.truncate_text(self.current_song.get("genre", "Unknown Genre"))
            )
        else:
            self.clear_right_frame_info()

    def clear_right_frame_info(self):
        """Clear the information displayed in the right frame."""
        self.song_picture.setPixmap(
            QPixmap("default.png").scaled(250, 250, Qt.KeepAspectRatio)
        )
        self.song_title_label.setText("Title:")
        self.song_author_label.setText("Author:")
        self.song_album_label.setText("Album:")
        self.song_genre_label.setText("Genre:")

    def update_progress(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            elapsed_time = self.media_player.position() // 1000  # milliseconds to seconds
            total_time = self.media_player.duration() // 1000
            elapsed_str = self.format_time(elapsed_time)
            total_str = self.format_time(total_time)
            self.time_label.setText(f"{elapsed_str} / {total_str}")
            if total_time > 0:
                self.progress_bar.setValue(int((elapsed_time / total_time) * 100))
            self.setWindowTitle(
                f"Iota Player • {self.current_playlist} ({len(self.songs)} songs) • {self.song_info_var} • {elapsed_str} / {total_str}"
            )

    def check_song_end(self):
        if self.has_started and self.media_player.state() != QMediaPlayer.PlayingState and self.current_song:
            if not self.is_paused:
                self.handle_song_end()
            else:
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
        # logging.info(f"Loop mode set to: {self.is_looping}")

    def shuffle_songs(self):
        if self.current_playlist:
            self.playlist_manager.shuffle_songs(self.current_playlist)
            self.is_shuffling = True
            self.shuffled_index = 0
            logging.info("Songs shuffled.")

    def toggle_shuffle(self):
        self.is_shuffling = not self.is_shuffling
        self.shuffle_button.setText(
            "Shuffle On" if self.is_shuffling else "Shuffle Off"
        )
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
        try:
            logging.info(f"Song ended. Looping: {self.is_looping}")
            if self.is_looping == "Song":
                self.play_music()
            elif self.is_looping == "Playlist":
                self.next_song()
            else:
                self.stop_music()
        except Exception as e:
            logging.error(f"Error in handle_song_end: {e}")

    def open_youtube(self):
        """Open the YouTube video for the current song."""
        if self.current_song and "youtube_id" in self.current_song:
            youtube_url = (
                f"https://www.youtube.com/watch?v={self.current_song['youtube_id']}"
            )
            webbrowser.open(youtube_url)
            logging.info(f"Opened YouTube video: {youtube_url}")

    def open_playlist_maker(self):
        logging.info("Opening Playlist Maker")
        self.playlist_maker_window = PlaylistMaker(self.icon_path)
        self.playlist_maker_window.show()
