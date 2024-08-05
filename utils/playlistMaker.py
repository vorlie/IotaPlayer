import re, logging, json, os, random
from PyQt5.QtWidgets import QDialog, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

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


class PlaylistMaker(QDialog):
    def __init__(self, icon_path):
        super().__init__()
        self.icon_path = icon_path
        self.setWindowTitle("Playlist Maker")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1200, 800)
        
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        
        self.initUI()
    
    def initUI(self):
        # Main layout
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Left frame layout
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)
        self.left_frame.setLayout(self.left_layout)
        self.left_frame.setFixedWidth(300)
        self.layout.addWidget(self.left_frame, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Folder selection
        self.folder_label = QLabel("Select folder containing songs:")
        self.left_layout.addWidget(self.folder_label)

        self.folder_path_label = QLabel("(folder name)")
        self.left_layout.addWidget(self.folder_path_label)

        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.setFixedWidth(150)
        self.select_folder_button.clicked.connect(self.select_folder)
        self.left_layout.addWidget(self.select_folder_button)

        # Playlist name input
        self.playlist_name_label = QLabel("Enter playlist name:")
        self.left_layout.addWidget(self.playlist_name_label)

        self.playlist_name_input = QLineEdit()
        self.left_layout.addWidget(self.playlist_name_input)

        # Add songs manually
        self.add_songs_label = QLabel("Add songs manually:")
        self.left_layout.addWidget(self.add_songs_label)

        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Artist")
        self.left_layout.addWidget(self.artist_input)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.left_layout.addWidget(self.title_input)

        self.youtube_id_input = QLineEdit()
        self.youtube_id_input.setPlaceholderText("YouTube ID")
        self.left_layout.addWidget(self.youtube_id_input)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Song Path")
        self.left_layout.addWidget(self.path_input)

        # Buttons for adding song and saving playlist
        self.button_layout = QHBoxLayout()
        self.left_layout.addLayout(self.button_layout)

        self.add_song_button = QPushButton("Add Song")
        self.add_song_button.clicked.connect(self.add_song)
        self.button_layout.addWidget(self.add_song_button)

        self.save_playlist_button = QPushButton("Save Playlist")
        self.save_playlist_button.clicked.connect(self.save_playlist)
        self.button_layout.addWidget(self.save_playlist_button)
        
        self.open_playlist_button = QPushButton("Open Existing Playlist")
        self.open_playlist_button.clicked.connect(self.open_playlist)
        self.button_layout.addWidget(self.open_playlist_button)

        self.note_information = QLabel(
            """
            <b>Notes:</b><br><br>
            <ul>
                <li><b>Select a folder</b> with songs to automatically populate the playlist or add songs manually.</li>
                <li><b>Add songs manually</b> by entering the artist, title, YouTube ID (optional), and song path.</li>
                <li><b>Use the full path</b> to the song file when adding manually.</li>
                <li><b>Follow the file naming format</b> for automatic recognition:<br>
                    <i>Artist - Title [YouTube ID].mp3</i><br>
                    Example: <i>Adele - Hello [dQw4w9WgXcQ].mp3</i>
                </li>
                <li><b>To delete a song</b>, select the row in the table and press the <b>Delete</b> key on your keyboard.</li>
                <li><b>Click on a row</b> in the table to select a song before performing any actions.</li>
                <li><b>Double-click</b> on a cell in the table to <b>edit</b> its content.</li>
            </ul>
            """
        )

        self.note_information.setWordWrap(True)
        self.left_layout.addWidget(self.note_information)
        
        # Right frame layout
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        self.layout.addWidget(self.right_frame)

        # Table view for song list
        self.song_table = QTableWidget()
        self.song_table.setColumnCount(4)
        self.song_table.setHorizontalHeaderLabels(["Artist", "Title", "YouTube ID", "Path"])
        self.right_layout.addWidget(self.song_table)
        self.song_table.setColumnWidth(0, 150)
        self.song_table.setColumnWidth(1, 150)
        self.song_table.setColumnWidth(2, 150)
        self.song_table.setColumnWidth(3, 300)
        self.song_table.itemChanged.connect(self.update_song_data)
        self.songs = []

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path_label.setText(folder)
            self.process_folder(folder)
    
    def process_folder(self, folder):
        self.songs = []
        self.song_table.setRowCount(0)
        song_files = [f for f in os.listdir(folder) if f.endswith(".mp3")]

        for filename in song_files:
            match = re.match(r'(.+) - (.+)(?: \[([^\]]*)\])?\.mp3', filename)
            if match:
                artist, title, youtube_id = match.groups()
                path = os.path.join(folder, filename)
                song_data = {
                    'artist': artist,
                    'title': title,
                    'youtube_id': youtube_id or '',  # Ensure youtube_id is an empty string if None
                    'path': path.replace('/', '\\')
                }
                self.songs.append(song_data)
                self.add_song_to_table(song_data)
            else:
                # Optionally log or handle files that don’t match the pattern
                logging.warning(f"File '{filename}' does not match the expected pattern.")

        # Optionally log the total number of songs processed
        logging.info(f"Processed {len(self.songs)} songs.")

    def add_song_to_table(self, song_data):
        row_position = self.song_table.rowCount()
        self.song_table.insertRow(row_position)
        self.song_table.setItem(row_position, 0, QTableWidgetItem(song_data['artist']))
        self.song_table.setItem(row_position, 1, QTableWidgetItem(song_data['title']))
        self.song_table.setItem(row_position, 2, QTableWidgetItem(song_data['youtube_id']))
        self.song_table.setItem(row_position, 3, QTableWidgetItem(song_data['path']))

    def add_song(self):
        artist = self.artist_input.text()
        title = self.title_input.text()
        youtube_id = self.youtube_id_input.text()
        path = self.path_input.text()
        if artist and title and path:
            song_data = {
                'artist': artist,
                'title': title,
                'youtube_id': youtube_id if youtube_id else '',
                'path': path.replace('/', '\\')
            }
            self.songs.append(song_data)
            self.add_song_to_table(song_data)
            self.artist_input.clear()
            self.title_input.clear()
            self.youtube_id_input.clear()
            self.path_input.clear()

    def save_playlist(self):
        playlist_name = self.playlist_name_input.text()
        if playlist_name and self.songs:
            # Add "playlist" field and "song_count" to each song entry
            for song in self.songs:
                song['playlist'] = playlist_name
            
            playlist_data = {
                "playlist_name": playlist_name,
                "song_count": len(self.songs), 
                "songs": self.songs
            }
            playlist_path = os.path.join(self.config.get('root_playlist_folder', "playlists"), f"{playlist_name}.json")
            with open(playlist_path, 'w') as f:
                json.dump(playlist_data, f, indent=4)
            QMessageBox.information(self, "Playlist Saved", f"Playlist '{playlist_name}' saved to {playlist_path}.")
            logging.info(f"Playlist saved to {playlist_path}")
            
    def open_playlist(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        
        # Define the directory where playlists are stored
        playlist_directory = self.config.get('root_playlist_folder', "playlists")

        # Open a file dialog to select a playlist
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Playlist", 
            playlist_directory, 
            "JSON Files (*.json);;All Files (*)", 
            options=options
        )
        
        # If a file was selected
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    playlist_data = json.load(f)
                    self.songs = playlist_data.get("songs", [])
                    self.update_table()
                    self.playlist_name_input.setText(playlist_data.get("playlist_name", ""))
                logging.info(f"Playlist loaded from {file_path}")
            except Exception as e:
                logging.error(f"Failed to load playlist: {e}")
                self.playlist_name_input.clear()

    def update_table(self):
        self.song_table.setRowCount(0)
        for song in self.songs:
            self.add_song_to_table(song)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_indexes = self.song_table.selectionModel().selectedRows()
            # Sort in reverse order to avoid issues with shifting rows
            for index in sorted(selected_indexes, reverse=True):
                row = index.row()
                self.song_table.removeRow(row)
                # Ensure that you delete the item from the self.songs list as well
                if row < len(self.songs):
                    del self.songs[row]

    def update_song_data(self, item):
        row = item.row()
        column = item.column()
        value = item.text()

        if column == 0:
            self.songs[row]['artist'] = value
        elif column == 1:
            self.songs[row]['title'] = value
        elif column == 2:
            self.songs[row]['youtube_id'] = value
        elif column == 3:
            self.songs[row]['path'] = os.path.normpath(value)
