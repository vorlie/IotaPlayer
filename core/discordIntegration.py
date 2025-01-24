from pypresence import Presence, ActivityType
import time, logging, json
from PyQt5.QtCore import QObject, pyqtSignal
from core.logger import setup_logging
from config import discord_cdn_images

discord_logger = logging.getLogger('discord')

class DiscordIntegration(QObject):
    connection_status_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        # Load config
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            self.client_id = self.config.get('discord_client_id', '1150680286649143356')
            #self.large_image_key = self.config.get('large_image_key', 'default_image')
            self.large_image_key = discord_cdn_images.get('default_image', 'https://cdn.discordapp.com/app-assets/1150680286649143356/1270124442433097780.png')
            self.connect_to_discord = self.config.get('connect_to_discord', True)
            self.use_playing_status = self.config.get('use_playing_status', False)
        
        self.RPC = None
        if self.connect_to_discord:
            self.connect()

    def connect(self):
        if not self.connect_to_discord:
            discord_logger.info("Discord integration is disabled.")
            return
        try:
            self.RPC = Presence(self.client_id)
            self.RPC.connect()
            discord_logger.info("Connected to Discord RPC.")
            self.connection_status_changed.emit(True)
        except Exception as e:
            discord_logger.error(f"Failed to connect to Discord RPC: {e}")
            self.RPC = None
            self.connection_status_changed.emit(False)

    def is_connected(self):
        return self.RPC is not None
    
    def update_presence(
        self, 
        song_title, 
        artist_name, 
        large_image_text, 
        small_image_key: str, 
        small_image_text: str, 
        youtube_id=None, 
        image_key=None, 
        song_duration=None,
        time_played=None):
        
        if not self.connect_to_discord:
            discord_logger.info("Discord integration is disabled. Skipping presence update.")
            return
        if not self.is_connected():
            discord_logger.warning("RPC not connected. Attempting to reconnect...")
            self.connect()
            if not self.is_connected():
                discord_logger.error("Unable to reconnect to Discord RPC.")
                return

        # Always include this button
        buttons = [{"label": "Source Code", "url": "https://github.com/vorlie/IotaPlayer"}]
        # Add an image key if specified
        if image_key is not None:
            large_image_key = image_key
        else: 
            large_image_key = self.large_image_key
        
        if self.use_playing_status is True:
            use_playing_status = ActivityType.PLAYING
        else: 
            use_playing_status = ActivityType.LISTENING
        
        # Conditionally add the YouTube button
        if youtube_id:
            buttons.append({"label": "Open in YouTube", "url": f"https://www.youtube.com/watch?v={youtube_id}"})
        try:
            if time_played is None:  # No time played, standard update
                self.RPC.update(
                    activity_type=use_playing_status,
                    state=f"{artist_name}",
                    details=f"{song_title}",
                    large_image=large_image_key,
                    large_text=large_image_text,
                    small_image=small_image_key,
                    small_text=small_image_text,
                    buttons=buttons
                )
                discord_logger.info(f"Presence updated: {song_title} by {artist_name}; Buttons: {buttons}")
            else:
                # Resuming from where it was paused
                start_time = int(time.time()) - int(time_played)  # Adjust start time based on played time
                end_time = start_time + song_duration  # Adjust end time
                discord_logger.info(f"DEBUG: Updating presence: song_duration={song_duration}, time_played={time_played}, start_time={start_time}, end_time={end_time}")
                self.RPC.update(
                    activity_type=use_playing_status,
                    state=f"{artist_name}",
                    details=f"{song_title}",
                    large_image=large_image_key,
                    large_text=large_image_text,
                    small_image=small_image_key,
                    small_text=small_image_text,
                    start=start_time,
                    end=end_time,
                    buttons=buttons
                )
                discord_logger.info(f"Presence updated: {song_title} by {artist_name}; Buttons: {buttons}; Start time: {start_time}; End time: {end_time}")
        except Exception as e:
            if "rate limit" in str(e).lower():
                discord_logger.warning(f"Rate limit hit: {e}. Waiting before retrying...")
                time.sleep(15)
                #self.update_presence(song_title, artist_name, song_duration, youtube_id)  # Retry after waiting
                self.update_presence(song_title, artist_name, large_image_text, small_image_key, small_image_text, youtube_id)
            else:
                discord_logger.error(f"Failed to update Discord presence: {e}")
                self.connect()

    def clear_presence(self):
        if not self.connect_to_discord:
            discord_logger.info("Discord integration is disabled. Skipping presence clear.")
            return
        if not self.is_connected():
            discord_logger.warning("RPC not connected. Attempting to reconnect...")
            self.connect()
            if not self.is_connected():
                discord_logger.error("Unable to reconnect to Discord RPC.")
                return

        try:
            self.RPC.clear()
            discord_logger.info("Presence cleared.")
        except Exception as e:
            discord_logger.error(f"Failed to clear Discord presence: {e}")
            self.connect()
