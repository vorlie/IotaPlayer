# IotaPlayer - A feature-rich music player application
# Copyright (C) 2025 Charlie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# core/discordIntegration.py
# =============
# Discord Integration for IotaPlayer
## This module implements Discord Rich Presence integration for IotaPlayer,
# allowing the player to display current song information,
# artist details, and playback status in Discord.
# =============
import os
import platform
from pypresence import Presence, ActivityType
import time
import logging
import json
from PyQt6.QtCore import QObject, pyqtSignal
from threading import Lock
from pydantic import BaseModel
from typing import Optional
from config import discord_cdn_images
from tenacity import retry, stop_after_attempt, wait_fixed

discord_logger = logging.getLogger('discord')

class PresenceUpdateData(BaseModel):
    song_title: str
    artist_name: str
    large_image_text: str
    small_image_key: str
    small_image_text: str
    youtube_id: Optional[str] = None
    image_key: Optional[str] = None
    song_duration: Optional[int] = None
    time_played: Optional[int] = None

def get_config_dir():
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "IotaPlayer")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "IotaPlayer")

class DiscordConfig:
    def __init__(self):
        config_dir = get_config_dir()
        with open(os.path.join(config_dir, 'config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.client_id = config.get('discord_client_id', '1150680286649143356')
        self.large_image_key = discord_cdn_images.get(
            'default_image', 
            'https://cdn.discordapp.com/app-assets/1150680286649143356/1270124442433097780.png'
        )
        self.connect_to_discord = config.get('connect_to_discord', True)
        self.base_buttons = [{"label": "Source Code", "url": "https://github.com/vorlie/IotaPlayer"}]

class DiscordIntegration(QObject):
    connection_status_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self.config = DiscordConfig()
        self.RPC = None
        self.current_large_image = self.config.large_image_key
        self.small_image_key = ""
        
        if self.config.connect_to_discord:
            self.connect()

    def connect(self):
        if not self.config.connect_to_discord:
            return

        with self._lock:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.RPC = Presence(self.config.client_id)
                    self.RPC.connect()
                    discord_logger.info("Connected to Discord RPC")
                    self.connection_status_changed.emit(True)
                    return
                except Exception as e:
                    wait_time = 2 ** attempt
                    discord_logger.warning(
                        f"Connection attempt {attempt+1}/{max_retries} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
            
            discord_logger.error("All connection attempts failed")
            self.connection_status_changed.emit(False)

    def is_connected(self):
        with self._lock:
            return self.RPC is not None

    def update_presence(self, update_data: PresenceUpdateData):
        if not self.config.connect_to_discord:
            return

        with self._lock:
            if not self._ensure_connection():
                return

            try:
                activity = self._create_base_activity(update_data)
                activity = self._handle_timestamps(activity, update_data)
                self._execute_presence_update(activity, update_data)
            except Exception as e:
                self._handle_update_error(e, update_data)

    def _create_base_activity(self, data: PresenceUpdateData) -> dict:
        activity = {
            'activity_type': ActivityType.LISTENING,
            'state': data.artist_name,
            'details': data.song_title,
            'large_image': data.image_key or self.current_large_image,
            'large_text': data.large_image_text,
            'small_image': data.small_image_key,
            'small_text': data.small_image_text,
            'buttons': self.config.base_buttons.copy()
        }

        if data.youtube_id:
            activity['buttons'].append({
                "label": "Open in YouTube",
                "url": f"https://www.youtube.com/watch?v={data.youtube_id}"
            })
        
        return activity

    def _handle_timestamps(self, activity: dict, data: PresenceUpdateData) -> dict:
        if data.time_played is not None and data.song_duration:
            current_time = int(time.time())
            activity['start'] = current_time - data.time_played
            activity['end'] = current_time + (data.song_duration - data.time_played)
        return activity

    def _execute_presence_update(self, activity: dict, data: PresenceUpdateData):
        self.RPC.update(**activity)
        discord_logger.info(
            f"Presence updated: {data.song_title} by {data.artist_name} | "
            f"Buttons: {len(activity['buttons'])} | "
            f"Timestamps: {bool(data.time_played)}"
        )

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
    def _handle_update_error(self, error: Exception, data: PresenceUpdateData):
        error_str = str(error).lower()
        if "rate limit" in error_str:
            discord_logger.warning(f"Rate limited: {error}. Retrying...")
            time.sleep(15)
            self.update_presence(data)
        elif "pipe was closed" in error_str or "the pipe was closed" in error_str:
            discord_logger.warning(f"Discord pipe closed: {error}. Reconnecting...")
            self.connect()
            # After reconnect, try updating presence again
            self.update_presence(data)
        else:
            discord_logger.error(f"Update failed: {error}")
            self.connect()

    def _ensure_connection(self) -> bool:
        if self.RPC is None:
            discord_logger.warning("Attempting reconnection...")
            self.connect()
        return self.RPC is not None

    def clear_presence(self):
        with self._lock:
            if not self.config.connect_to_discord or not self.is_connected():
                return

            try:
                self.RPC.clear()
                discord_logger.info("Presence cleared")
            except Exception as e:
                discord_logger.error(f"Clear failed: {e}")
                self.connect()
