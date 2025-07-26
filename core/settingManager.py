## core/settingManager.py
# =============
# This module provides the settings dialog UI 
# and logic for IotaPlayer, including configuration tabs and saving/loading settings.
# =============
import os
import json
import subprocess
import sys
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QTabWidget, QFormLayout, QCheckBox, 
    QMessageBox, QApplication, QColorDialog, QSpinBox, QProgressBar 
)
from PyQt6.QtGui import QIcon
from core.coverArtExtractor import CoverArtExtractor
from core.imageCache import CoverArtCache

class SettingsDialog(QDialog):
    def __init__(self, settings, icon_path, config_path):
        super().__init__()
        self.settings = settings
        self.config_path = config_path
        self.icon_path = icon_path
        self.setWindowTitle("Iota Player • Settings")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        self.load_settings()
        self.initUI()

    def load_settings(self):
        """Load settings from the config file if it exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.settings = json.load(f)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Failed to load settings from the configuration file.")

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- General Tab ---
        self.general_tab = QWidget()
        self.general_layout = QFormLayout()
        self.general_tab.setLayout(self.general_layout)
        self.tabs.addTab(self.general_tab, "General")

        self.root_playlist_folder_edit = QLineEdit()
        self.root_playlist_folder_edit.setPlaceholderText("playlists")
        self.root_playlist_folder_edit.setText(self.settings.get("root_playlist_folder", "playlists"))
        self.root_playlist_browse_button = QPushButton("Browse")
        def browse_root_playlist_folder():
            from PyQt6.QtWidgets import QFileDialog
            folder = QFileDialog.getExistingDirectory(self, "Select Root Playlist Folder")
            if folder:
                self.root_playlist_folder_edit.setText(folder)
        self.root_playlist_browse_button.clicked.connect(browse_root_playlist_folder)
        root_playlist_layout = QHBoxLayout()
        root_playlist_layout.addWidget(self.root_playlist_folder_edit)
        root_playlist_layout.addWidget(self.root_playlist_browse_button)
        self.general_layout.addRow(QLabel("Root Playlist Folder:"), root_playlist_layout)

        self.default_playlist_edit = QLineEdit()
        self.default_playlist_edit.setPlaceholderText("default")
        self.default_playlist_edit.setText(self.settings.get("default_playlist", "default"))
        self.volume_percentage_edit = QSpinBox()
        self.volume_percentage_edit.setRange(0, 100)
        self.volume_percentage_edit.setValue(self.settings.get("volume_percentage", 100))
        self.general_layout.addRow(QLabel("Default Playlist:"), self.default_playlist_edit)
        self.general_layout.addRow(QLabel("Volume Percentage:"), self.volume_percentage_edit)

        self.unsorted_music_folder_edit = QLineEdit()
        self.unsorted_music_folder_edit.setPlaceholderText("Path to your unsorted music folder")
        self.unsorted_music_folder_edit.setText(self.settings.get("unsorted_music_folder", ""))
        self.unsorted_music_browse_button = QPushButton("Browse")
        def browse_unsorted_folder():
            from PyQt6.QtWidgets import QFileDialog
            folder = QFileDialog.getExistingDirectory(self, "Select Unsorted Music Folder")
            if folder:
                self.unsorted_music_folder_edit.setText(folder)
        self.unsorted_music_browse_button.clicked.connect(browse_unsorted_folder)
        unsorted_layout = QHBoxLayout()
        unsorted_layout.addWidget(self.unsorted_music_folder_edit)
        unsorted_layout.addWidget(self.unsorted_music_browse_button)
        self.general_layout.addRow(QLabel("Unsorted Music Folder:"), unsorted_layout)

        # --- Appearance Tab ---
        self.appearance_tab = QWidget()
        self.appearance_layout = QFormLayout()
        self.appearance_tab.setLayout(self.appearance_layout)
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        self.color_disclaimer_label = QLabel(
            "Note: Custom themes require 'qdarktheme' to be enabled for the application's overall theme.\n"
            "If 'qdarktheme' is disabled, the application will use the system's Qt6 theme (common on Linux/KDE).\n"
            "To enable 'qdarktheme', uncomment line 144 in 'main.py' and rebuild the application for changes to take effect."
        )

        self.color_disclaimer_label.setStyleSheet("font-weight: bold; border-radius: 5px; padding: 5px; background-color: #333333; ")

        self.font_name_edit = QLineEdit()
        self.font_name_edit.setPlaceholderText("Noto Sans")
        self.font_name_edit.setText(self.settings.get("font_name", "Noto Sans"))
        self.colorization_color_edit = QLineEdit()  
        self.colorization_color_edit.setPlaceholderText("automatic or #RRGGBB")
        color = self.settings.get("colorization_color", "automatic")
        if color.startswith("#"):
            self.colorization_color_edit.setText(color)
        else:
            self.colorization_color_edit.setText("")
        self.color_picker_button = QPushButton("Pick Color")
        self.color_picker_button.clicked.connect(self.open_color_picker)
        self.use_system_accent_checkbox = QCheckBox("Use System Accent Color")
        self.use_system_accent_checkbox.setChecked(color == "automatic")
        self.use_system_accent_checkbox.stateChanged.connect(self.toggle_colorization_color)
        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        self.dark_mode_checkbox.setChecked(self.settings.get("dark_mode", False))

        self.appearance_layout.addRow(QLabel("Font Name:"), self.font_name_edit)
        self.appearance_layout.addRow(self.use_system_accent_checkbox)
        self.appearance_layout.addRow(QLabel("Colorization Color:"), self.colorization_color_edit)
        self.appearance_layout.addRow(self.color_picker_button, QLabel())
        if sys.platform.startswith("linux"):
            self.appearance_layout.addRow(self.dark_mode_checkbox)
        
        self.appearance_layout.addRow(self.color_disclaimer_label)
        
        # --- Discord Tab ---
        self.discord_tab = QWidget()
        self.discord_layout = QFormLayout()
        self.discord_tab.setLayout(self.discord_layout)
        self.tabs.addTab(self.discord_tab, "Discord")

        self.connect_to_discord_checkbox = QCheckBox("Connect to Discord")
        self.connect_to_discord_checkbox.setChecked(self.settings.get("connect_to_discord", True))
        self.discord_client_id_edit = QLineEdit()
        self.discord_client_id_edit.setText(self.settings.get("discord_client_id", "1150680286649143356"))
        self.large_image_key_edit = QLineEdit()
        self.large_image_key_edit.setText(self.settings.get("large_image_key", "https://i.pinimg.com/564x/d5/ed/93/d5ed93e12eab198b830bc91f1ddf2dcb.jpg"))
        self.use_playing_status_edit = QCheckBox("Use Playing Status")
        self.use_playing_status_edit.setChecked(self.settings.get("use_playing_status", False))
        self.discord_layout.addRow(self.connect_to_discord_checkbox)
        self.discord_layout.addRow(self.use_playing_status_edit)
        self.discord_layout.addRow(QLabel("Discord Client ID:"), self.discord_client_id_edit)
        self.discord_layout.addRow(QLabel("Large Image Key:"), self.large_image_key_edit)

        # --- Google Tab ---
        self.google_tab = QWidget()
        self.google_layout = QFormLayout()
        self.google_tab.setLayout(self.google_layout)
        self.tabs.addTab(self.google_tab, "Google")

        self.google_client_secret_edit = QLineEdit()
        self.google_client_secret_edit.setPlaceholderText("Path to client_secret.json")
        self.google_client_secret_edit.setText(self.settings.get("google_client_secret_file", ""))
        self.google_layout.addRow(QLabel("Client Secret File:"), self.google_client_secret_edit)

        # --- Cover Art Tab ---
        self.cover_tab = QWidget()
        self.cover_layout = QVBoxLayout()
        self.cover_tab.setLayout(self.cover_layout)
        self.tabs.addTab(self.cover_tab, "Cover Art")

        # Add a title/description
        self.cover_layout.addWidget(QLabel("<b>Cover Art Extraction & Caching</b>"))
        self.cover_layout.addWidget(QLabel("Extract and cache album art for your music library. Existing covers will be skipped."))

        # Use a horizontal layout for button and progress bar
        cover_controls_layout = QHBoxLayout()
        self.extract_button = QPushButton("Extract & Cache Covers")
        cover_controls_layout.addWidget(self.extract_button)
        self.cover_progress = QProgressBar()
        self.cover_progress.setValue(0)
        self.cover_progress.setMinimumWidth(200)
        cover_controls_layout.addWidget(self.cover_progress)
        self.cover_layout.addLayout(cover_controls_layout)

        self.extract_button.clicked.connect(self.start_cover_extraction)
        self.cover_layout.addStretch(1)  # Add stretch to push controls to the top

        # --- Save/Cancel Buttons ---
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.close)

        # Initialize UI state
        self.toggle_colorization_color()

    def start_cover_extraction(self):
        music_dirs = [self.root_playlist_folder_edit.text()]
        self.cover_cache = CoverArtCache()  # You may want to pass a custom cache dir
        self.cover_thread = CoverArtExtractor(music_dirs, self.cover_cache)
        self.cover_thread.progress.connect(self.update_cover_progress)
        self.cover_thread.finished.connect(self.cover_extraction_finished)
        self.cover_thread.start()
        self.extract_button.setEnabled(False)

    def update_cover_progress(self, current, total):
        self.cover_progress.setMaximum(total)
        self.cover_progress.setValue(current)

    def cover_extraction_finished(self):
        self.extract_button.setEnabled(True)
        QMessageBox.information(self, "Done", "Cover extraction and caching finished.")

    def toggle_colorization_color(self):
        is_checked = self.use_system_accent_checkbox.isChecked()
        self.colorization_color_edit.setEnabled(not is_checked)
        self.color_picker_button.setEnabled(not is_checked)
        if is_checked:
            self.colorization_color_edit.setText("automatic")
            
    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colorization_color_edit.setText(color.name())

    def save_settings(self):
        self.settings["root_playlist_folder"] = self.root_playlist_folder_edit.text()
        self.settings["default_playlist"] = self.default_playlist_edit.text()
        
        if self.use_system_accent_checkbox.isChecked():
            self.settings["colorization_color"] = "automatic"
        else:
            color = self.colorization_color_edit.text()
            if color.startswith("#"):
                self.settings["colorization_color"] = color
            else:
                QMessageBox.warning(self, "Invalid Color", "Please enter a valid hex color code.")
                return
        
        self.settings["connect_to_discord"] = self.connect_to_discord_checkbox.isChecked()
        self.settings["discord_client_id"] = self.discord_client_id_edit.text()
        self.settings["large_image_key"] = self.large_image_key_edit.text()
        self.settings["use_playing_status"] = self.use_playing_status_edit.isChecked()
        self.settings["google_client_secret_file"] = self.google_client_secret_edit.text()
        self.settings["font_name"] = self.font_name_edit.text()
        self.settings["unsorted_music_folder"] = self.unsorted_music_folder_edit.text()
        
        if sys.platform.startswith("linux"):
            self.settings["dark_mode"] = self.dark_mode_checkbox.isChecked()
            
        # Validate volume input
        volume_input = self.volume_percentage_edit.text()
        try:
            volume = int(volume_input)
            if 0 <= volume <= 100:
                self.settings["volume_percentage"] = volume
            else:
                QMessageBox.warning(self, "Invalid Volume", "Please enter a volume between 0 and 100.")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter only numbers for the volume.")
            return
        # Save settings to file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)
        
        reply = QMessageBox.question(
            self, 'Restart Required',
            'Changes will not take effect until the application is restarted. Do you want to restart now?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.restart_application()
        else:
            self.accept()  # Close the dialog
            
    def restart_application(self):
        """Restart the application."""
        QApplication.quit()  # Close the application

        # Relaunch the application
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit()