# Changelog

## [1.11.0] - 2025-12-22

### Added
- **ConfigManager**: Centralized configuration management to ensure consistency and thread safety.
- **PlayerStateMachine**: Robust enum-based state machine for playback control, replacing inconsistent boolean flags.
- **Discord Update Queue**: Queue system for Discord Rich Presence to prevent lost updates during disconnections.
- **File-based Locking**: Robust single-instance enforcement using `fcntl` to prevent race conditions.
- **Environment Configuration**: Added support for `DISCORD_CLIENT_ID` environment variable.

### Changed
- **Refactoring**: Removed global `player` variable from `main.py` and introduced `Application` class.
- **Optimization**: Optimized configuration loading to reduce file I/O by passing config objects.
- **Startup**: Moved Qt version compatibility check to early startup phase to catch theme issues sooner.
- **Keyboard Handling**: Migrated keyboard listener to use Qt signals for thread-safe UI interaction.

### Fixed
- Fixed race condition in single-instance application check.
- Fixed `AttributeError` crashes caused by removed boolean flags (`has_started`, `is_paused`).
- Fixed `NameError` in Playlist Maker due to removed `get_config_path` function.
- Fixed invalid state transitions in playback logic (e.g., `STOPPED` -> `PLAYING`).
- Fixed application crash when `icon.png` is missing (now logs a warning).
- Fixed thread safety violations in keyboard listener.

## [1.10.12] - 2025-09-05

### Refactored
- Refactored the update dialog into multiple functions for better organization and maintainability.

### Added
- Added Changelog to the update dialog.

## [1.10.11] - 2025-09-05

### Fixed
- Improved the 'About' dialog's layout and functionality for better readability.
- The version checker is now more robust and can correctly detect a newer system Qt version, even with distribution-specific naming conventions.

## [1.10.10] - 2025-09-05

### Fixed
- Resolved an issue where the application theme was not applying correctly due to a version mismatch between PyQt6 and the system's Qt6 libraries (6.9.1 -> 6.9.2).