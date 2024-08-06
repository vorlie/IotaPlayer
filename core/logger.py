import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Root logger configuration
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():  # Check if handlers are already set up
        root_logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler
        file_handler = RotatingFileHandler('combined_app.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Discord logger configuration
    discord_logger = logging.getLogger('discord')
    if not discord_logger.hasHandlers():  # Check if handlers are already set up
        discord_logger.setLevel(logging.DEBUG)
        discord_logger.addHandler(file_handler)