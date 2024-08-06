import os, json, subprocess, sys
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QTabWidget, QFormLayout, QCheckBox, QMessageBox, QApplication, QColorDialog )
from PyQt5.QtGui import QIcon


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

        # Create tabs
        self.general_tab = QWidget()
        self.discord_tab = QWidget()
        
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.discord_tab, "Discord")

        # Layouts for each tab
        self.general_layout = QFormLayout()
        self.discord_layout = QFormLayout()

        self.general_tab.setLayout(self.general_layout)
        self.discord_tab.setLayout(self.discord_layout)

        # General settings
        self.root_playlist_folder_edit = QLineEdit()
        self.root_playlist_folder_edit.setPlaceholderText("playlists")
        self.root_playlist_folder_edit.setText(self.settings.get("root_playlist_folder", "playlists"))
        
        self.default_playlist_edit = QLineEdit()
        self.default_playlist_edit.setPlaceholderText("default")
        self.default_playlist_edit.setText(self.settings.get("default_playlist", "default"))

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
        
        self.general_layout.addRow(QLabel("Root Playlist Folder:"), self.root_playlist_folder_edit)
        self.general_layout.addRow(QLabel("Default Playlist:"), self.default_playlist_edit)
        self.general_layout.addRow(self.use_system_accent_checkbox)
        self.general_layout.addRow(QLabel("Colorization Color:"), self.colorization_color_edit)
        self.general_layout.addRow(self.color_picker_button, QLabel())
        
        # Discord settings
        self.connect_to_discord_checkbox = QCheckBox("Connect to Discord")
        self.connect_to_discord_checkbox.setChecked(self.settings.get("connect_to_discord", True))
        
        self.discord_client_id_edit = QLineEdit()
        self.discord_client_id_edit.setText(self.settings.get("discord_client_id", "1150680286649143356"))
        
        self.large_image_key_edit = QLineEdit()
        self.large_image_key_edit.setText(self.settings.get("large_image_key", "https://i.pinimg.com/564x/d5/ed/93/d5ed93e12eab198b830bc91f1ddf2dcb.jpg"))
        
        self.use_playing_status_edit = QCheckBox("Use Playing Status")
        self.use_playing_status_edit.setChecked(self.settings.get("use_playing_status", False))
        
        self.discord_layout.addRow(self.connect_to_discord_checkbox, QLabel())
        self.discord_layout.addRow(self.use_playing_status_edit, QLabel())
        self.discord_layout.addRow(QLabel("Discord Client ID:"), self.discord_client_id_edit)
        self.discord_layout.addRow(QLabel("Large Image Key:"), self.large_image_key_edit)
        
        # Buttons
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
        
        # Save settings to file
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
        
        reply = QMessageBox.question(
            self, 'Restart Required',
            'Changes will not take effect until the application is restarted. Do you want to restart now?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.restart_application()
        else:
            self.accept()  # Close the dialog
            
    def restart_application(self):
        """Restart the application."""
        QApplication.quit()  # Close the application

        # Relaunch the application
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit()