from pypresence import Presence
import time, logging, json
from PyQt5.QtCore import QObject, pyqtSignal
from core.logger import setup_logging

discord_logger = logging.getLogger('discord')

class DiscordIntegration(QObject):
    connection_status_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        # Load config
        with open('config.json', 'r') as f:
            self.config = json.load(f)
            self.discord_client_id = self.config.get('discord_client_id', '1150680286649143356')
            self.large_image_key = self.config.get('large_image_key', 'https://i.pinimg.com/564x/d5/ed/93/d5ed93e12eab198b830bc91f1ddf2dcb.jpg')
            self.connect_to_discord = self.config.get('connect_to_discord', True)
        
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

    def update_presence(self, song_title, artist_name, song_duration, youtube_id=None, is_playing=True):
        if not self.connect_to_discord:
            discord_logger.info("Discord integration is disabled. Skipping presence update.")
            return
        if not self.is_connected():
            discord_logger.warning("RPC not connected. Attempting to reconnect...")
            self.connect()
            if not self.is_connected():
                discord_logger.error("Unable to reconnect to Discord RPC.")
                return

        start_time = int(time.time())
        end_time = int(start_time + song_duration)

        buttons = [{"label": "Open in YouTube", "url": f"https://www.youtube.com/watch?v={youtube_id}"}] if youtube_id else []
        
        try:
            self.RPC.update(
                state=f"{artist_name}",
                details=f"{song_title}",
                large_image=self.large_image_key,
                large_text="Music Player",
                start=start_time,
                end=end_time,
                buttons=buttons if youtube_id else None 
            )
            discord_logger.info(f"Presence updated: {song_title} by {artist_name}; Buttons: {buttons}; Start time: {start_time}; End time: {end_time}")
        except Exception as e:
            if "rate limit" in str(e).lower():
                discord_logger.warning(f"Rate limit hit: {e}. Waiting before retrying...")
                time.sleep(15)
                self.update_presence(song_title, artist_name, song_duration, youtube_id)  # Retry after waiting
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