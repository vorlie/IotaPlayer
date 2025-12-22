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

# core/configManager.py
# =============
# Centralized configuration management for IotaPlayer.
# Provides thread-safe singleton access to configuration operations,
# eliminating code duplication and ensuring consistent config handling.
# =============

import os
import json
import platform
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Singleton configuration manager for IotaPlayer.
    
    Provides centralized, thread-safe access to configuration operations including
    path resolution, config loading/saving, and caching to reduce file I/O.
    
    Usage:
        config_mgr = ConfigManager.get_instance()
        config = config_mgr.load_config()
        config_mgr.save_config(updated_config)
    """
    
    _instance: Optional['ConfigManager'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize ConfigManager. Use get_instance() instead of direct instantiation."""
        if ConfigManager._instance is not None:
            raise RuntimeError("Use ConfigManager.get_instance() to get the singleton instance")
        
        self._config_cache: Optional[Dict[str, Any]] = None
        self._cache_lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """
        Get the singleton instance of ConfigManager.
        
        Thread-safe singleton implementation using double-checked locking.
        
        Returns:
            ConfigManager: The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_config_dir(self) -> str:
        """
        Get the configuration directory path based on the operating system.
        
        Returns:
            str: Absolute path to the configuration directory
                 - Windows: %APPDATA%/IotaPlayer
                 - Linux/Unix: ~/.config/IotaPlayer
        """
        if platform.system() == "Windows":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
            return os.path.join(base, "IotaPlayer")
        else:
            return os.path.join(os.path.expanduser("~"), ".config", "IotaPlayer")
    
    def get_config_path(self) -> str:
        """
        Get the full path to the config.json file.
        
        Returns:
            str: Absolute path to config.json
        """
        return os.path.join(self.get_config_dir(), "config.json")
    
    def load_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load configuration from config.json.
        
        Args:
            use_cache: If True, return cached config if available (default: True)
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist and no defaults available
            json.JSONDecodeError: If config file contains invalid JSON
        """
        with self._cache_lock:
            # Return cached config if available and cache is enabled
            if use_cache and self._config_cache is not None:
                self._logger.debug("Returning cached configuration")
                return self._config_cache.copy()
            
            config_path = self.get_config_path()
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._config_cache = config
                    self._logger.info(f"Loaded configuration from {config_path}")
                    return config.copy()
            except FileNotFoundError:
                self._logger.warning(f"Config file not found at {config_path}")
                raise
            except json.JSONDecodeError as e:
                self._logger.error(f"Invalid JSON in config file: {e}")
                raise
    
    def save_config(self, config: Dict[str, Any], atomic: bool = True) -> None:
        """
        Save configuration to config.json.
        
        Args:
            config: Configuration dictionary to save
            atomic: If True, use atomic write (write to temp file, then rename)
        
        Raises:
            IOError: If unable to write config file
        """
        config_path = self.get_config_path()
        config_dir = self.get_config_dir()
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        try:
            if atomic:
                # Atomic write: write to temp file, then rename
                temp_path = config_path + ".tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                
                # Atomic rename (overwrites existing file)
                if platform.system() == "Windows":
                    # Windows requires removing the target file first
                    if os.path.exists(config_path):
                        os.remove(config_path)
                os.rename(temp_path, config_path)
            else:
                # Direct write
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
            
            # Update cache
            with self._cache_lock:
                self._config_cache = config.copy()
            
            self._logger.info(f"Saved configuration to {config_path}")
        except IOError as e:
            self._logger.error(f"Error saving config: {e}")
            raise
    
    def invalidate_cache(self) -> None:
        """
        Invalidate the cached configuration.
        
        Next call to load_config() will reload from disk.
        """
        with self._cache_lock:
            self._config_cache = None
            self._logger.debug("Configuration cache invalidated")
    
    def ensure_config_exists(self, default_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure configuration file exists, creating it with defaults if needed.
        
        Args:
            default_config: Default configuration to use if file doesn't exist
        
        Returns:
            Dict[str, Any]: Loaded or newly created configuration
        """
        try:
            return self.load_config(use_cache=False)
        except FileNotFoundError:
            self._logger.info("Config file not found, creating with defaults")
            self.save_config(default_config)
            return default_config.copy()
