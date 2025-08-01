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

# core/logger.py
# =============
# This module configures logging for IotaPlayer, including console and file handlers.
# It also sets up a Discord logger for integration with Discord Rich Presence.
# The log files are stored in a user-specific configuration directory,
# which varies based on the operating system (Windows or Unix-like).
# =============
import logging
from logging.handlers import RotatingFileHandler
import os
import platform

def get_config_dir():
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "IotaPlayer")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "IotaPlayer")

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

        # File handler in config dir
        log_dir = get_config_dir()
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'combined_app.log')
        file_handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Discord logger configuration
    discord_logger = logging.getLogger('discord')
    if not discord_logger.hasHandlers():  # Check if handlers are already set up
        discord_logger.setLevel(logging.DEBUG)
        discord_logger.addHandler(file_handler)