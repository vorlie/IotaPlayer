# IotaPlayer - TODO & Improvements

> **Last Updated:** 2025-12-22  
> **Version:** 1.11.0

This document outlines code improvements, performance optimizations, architectural enhancements, and potential bug fixes for IotaPlayer.

---

## Table of Contents

- [Critical Issues & Bug Fixes](#critical-issues--bug-fixes)
- [Architecture & Code Quality](#architecture--code-quality)
- [Performance Optimizations](#performance-optimizations)
- [UI/UX Improvements](#uiux-improvements)
- [Feature Enhancements](#feature-enhancements)
- [Code Maintenance](#code-maintenance)

---

## Critical Issues & Bug Fixes

### 🔴 High Priority

- [ ] **Global Variable in main.py** (Line 183)
  - Issue: `global player` is used, making the player instance globally accessible
  - Impact: Poor encapsulation, potential memory leaks, difficult to test
  - Solution: Refactor to return player instance or use class-based structure
  - File: `main.py:183`

- [ ] **Race Condition in Single Instance Check** (Line 144-146)
  - Issue: Between checking if instance is running and setting up server, another instance could start
  - Impact: Multiple instances could potentially run
  - Solution: Use file-based lock or atomic server creation
  - File: `main.py:144-150`

- [ ] **Unsafe Config Loading in Multiple Locations**
  - Issue: `get_config_dir()` and config loading duplicated across 5+ files
  - Impact: Inconsistent config handling, harder to maintain
  - Solution: Create centralized `ConfigManager` class
  - Files: `config.py`, `logger.py`, `discordIntegration.py`, `imageCache.py`, `google.py`, `playlistMaker.py`

- [ ] **Discord Presence Update Without Connection Check**
  - Issue: Discord updates may fire before connection is established
  - Impact: Potential crashes or silent failures
  - Solution: Queue updates until connection confirmed
  - File: `core/discordIntegration.py:113-126`

- [ ] **Media Player State Not Properly Tracked**
  - Issue: Multiple state variables (`is_playing`, `is_paused`, `has_started`) can become inconsistent
  - Impact: UI buttons showing wrong state, playback issues
  - Solution: Use enum-based state machine
  - File: `core/musicPlayer.py:352-381`

- [ ] **Thread Safety Issues**
  - Issue: `keyboard.Listener` thread accesses UI elements directly
  - Impact: Potential Qt thread safety violations
  - Solution: Use Qt signals to communicate from listener thread
  - File: `core/musicPlayer.py:334-336`

### 🟡 Medium Priority

- [ ] **No Error Handling for Missing Icon Files**
  - Issue: If icon files missing, app continues without icon silently
  - Impact: Poor UX, no feedback to user
  - Solution: Log warning and use fallback icon
  - File: `main.py:24-26`, `config.py:23-26`

- [ ] **Hardcoded Discord Client ID**
  - Issue: Discord client ID hardcoded in default settings
  - Impact: Difficult to change for forks/distributions
  - Solution: Make it configurable via environment variable
  - File: `config.py:32`

- [ ] **Version Comparison Duplicated**
  - Issue: `is_version_higher()` exists in both `config.py` and `AboutDialog`
  - Impact: Code duplication, maintenance burden
  - Solution: Use single implementation from config module
  - Files: `config.py:120-141`, `core/musicPlayer.py:225-245`

- [ ] **Qt Version Check Happens Too Late**
  - Issue: Version compatibility check after QApplication created
  - Impact: Theme issues may already manifest
  - Solution: Check before QApplication initialization
  - File: `main.py:91-119`, `main.py:142-153`

- [ ] **Config File Repeatedly Opened**
  - Issue: Config file loaded separately in multiple classes
  - Impact: File I/O overhead, potential inconsistencies
  - Solution: Load once and pass to components
  - Files: `main.py:121`, `core/musicPlayer.py:308`, `core/discordIntegration.py:64`

---

## Architecture & Code Quality

### Code Structure

- [ ] **Separate Business Logic from UI** (Lines 293-1636)
  - Issue: `MusicPlayer` class is 1600+ lines mixing UI and logic
  - Solution: Extract to separate classes:
    - `PlayerState` - manages playback state
    - `PlayerUI` - handles UI components
    - `PlayerController` - coordinates between them
  - File: `core/musicPlayer.py`

- [ ] **Create Dedicated Config Manager**
  ```python
  class ConfigManager:
      _instance = None
      
      @classmethod
      def get_instance(cls):
          if cls._instance is None:
              cls._instance = cls()
          return cls._instance
      
      def get_config_dir(self):
          # Centralized implementation
      
      def load_config(self):
          # Centralized loading with caching
  ```
  - Files: Create new `core/configManager.py`

- [ ] **Extract Constants to Configuration File**
  - Issue: Magic numbers and strings throughout code
  - Examples: Timer intervals (1000, 100, 10000ms), button widths (70px), frame widths (300px, 270px)
  - Solution: Create `core/constants.py` or move to config
  - Files: `core/musicPlayer.py:364-373, 466, 476, 594, 649`

- [ ] **Implement Proper Dependency Injection**
  - Issue: Components create their own dependencies
  - Example: `DiscordIntegration` creates `DiscordConfig` internally
  - Solution: Pass dependencies through constructor
  - File: `core/discordIntegration.py:74-83`

### Error Handling

- [ ] **Add Custom Exception Classes**
  ```python
  class IotaPlayerException(Exception):
      pass
  
  class ConfigurationError(IotaPlayerException):
      pass
  
  class PlaylistError(IotaPlayerException):
      pass
  
  class DiscordConnectionError(IotaPlayerException):
      pass
  ```
  - Files: Create new `core/exceptions.py`

- [ ] **Improve Exception Handling in Config Loading**
  - Issue: Broad `except Exception` catches everything
  - Solution: Catch specific exceptions, provide meaningful errors
  - Files: `main.py:122-127`, `config.py:82-87, 104-109`

- [ ] **Add Retry Logic for Network Operations**
  - Issue: Version check and Discord connection fail silently
  - Solution: Implement exponential backoff retry
  - Files: `config.py:102-118`, `core/discordIntegration.py:85-107`

### Type Safety

- [ ] **Add Type Hints Throughout Codebase**
  - Issue: Most functions lack type annotations
  - Solution: Add comprehensive type hints:
  ```python
  from typing import Optional, List, Dict, Tuple
  
  def load_config() -> Dict[str, Any]:
      ...
  
  def get_playlist_names(self) -> List[Tuple[str, str, int, str]]:
      ...
  ```
  - Files: All Python files

- [ ] **Use Pydantic for Configuration Validation**
  - Issue: No validation of config values
  - Solution: Create Pydantic models for settings
  ```python
  from pydantic import BaseModel, validator
  
  class AppSettings(BaseModel):
      volume_percentage: int
      connect_to_discord: bool
      
      @validator('volume_percentage')
      def validate_volume(cls, v):
          if not 0 <= v <= 100:
              raise ValueError('Volume must be 0-100')
          return v
  ```
  - File: `config.py`

### Logging

- [ ] **Improve Logging Structure**
  - Issue: Inconsistent logging, missing context
  - Solution: 
    - Use structured logging with context
    - Add correlation IDs for request tracking
    - Use different log levels appropriately
  - Files: All files using `logging`

- [ ] **Add Performance Logging**
  - Issue: No performance metrics tracked
  - Solution: Log slow operations (>100ms)
  ```python
  import functools
  import time
  
  def log_performance(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
          start = time.time()
          result = func(*args, **kwargs)
          duration = time.time() - start
          if duration > 0.1:
              logging.warning(f"{func.__name__} took {duration:.2f}s")
          return result
      return wrapper
  ```

---

## Performance Optimizations

### Memory Management

- [ ] **Implement Cover Art Cache Expiry**
  - Issue: `CoverArtCache` grows indefinitely in memory
  - Impact: Memory leak over long sessions
  - Solution: Implement LRU cache with size limit
  ```python
  from functools import lru_cache
  from collections import OrderedDict
  
  class LRUCache(OrderedDict):
      def __init__(self, maxsize=128):
          self.maxsize = maxsize
          super().__init__()
  ```
  - File: `core/imageCache.py:37-44`

- [ ] **Lazy Load Discord Integration**
  - Issue: Discord connection attempted even if disabled in config
  - Solution: Only initialize when `connect_to_discord` is True
  - File: `core/musicPlayer.py:338`

- [ ] **Optimize Playlist Loading**
  - Issue: All playlists loaded at startup even if not used
  - Solution: Load playlists on-demand
  - File: `core/playlistMaker.py:45-64`

### Database/Storage

- [ ] **Consider SQLite for Playlist Storage**
  - Issue: JSON files slow for large playlists, no indexing
  - Benefits:
    - Faster queries and searches
    - Built-in indexing
    - ACID transactions
    - Better concurrent access
  - Migration: Create migration script for existing JSON files

- [ ] **Implement Metadata Caching**
  - Issue: Song metadata read from files repeatedly
  - Solution: Cache metadata in SQLite database
  - Benefits: Faster playlist loading, reduced I/O

### UI Rendering

- [ ] **Debounce Search Input**
  - Issue: Search fires on every keystroke
  - Impact: Unnecessary UI updates, lag on large libraries
  - Solution: Add 300ms debounce
  ```python
  from PyQt6.QtCore import QTimer
  
  class DebouncedLineEdit(QLineEdit):
      def __init__(self):
          super().__init__()
          self.debounce_timer = QTimer()
          self.debounce_timer.setSingleShot(True)
          self.debounce_timer.timeout.connect(self.on_search)
          self.textChanged.connect(self.start_debounce)
      
      def start_debounce(self):
          self.debounce_timer.start(300)
  ```
  - File: `core/musicPlayer.py:566-568`

- [ ] **Virtualize Song List for Large Libraries**
  - Issue: QListWidget loads all items at once
  - Impact: Slow with 1000+ songs
  - Solution: Use QTableView with custom model for virtualization
  - File: `core/musicPlayer.py:584`

- [ ] **Optimize Cover Art Loading**
  - Issue: Images processed synchronously on main thread
  - Solution: Load and process images in background thread
  - File: `core/imageCache.py:59-74`

### Network Operations

- [ ] **Add Connection Pooling for API Requests**
  - Issue: Each request creates new connection
  - Solution: Use `requests.Session()` for connection reuse
  - Files: `config.py:83, 105`

- [ ] **Cache Version Check Results**
  - Issue: Update check runs every startup
  - Solution: Cache for 24 hours
  - File: `core/musicPlayer.py:391-394`

---

## UI/UX Improvements

### Layout & Design

- [ ] **Responsive Layout System**
  - Issue: Fixed widths (300px, 270px) don't adapt to screen size
  - Solution: Use proportional sizing with QSplitter
  ```python
  splitter = QSplitter(Qt.Orientation.Horizontal)
  splitter.addWidget(left_frame)
  splitter.addWidget(middle_frame)
  splitter.addWidget(right_frame)
  splitter.setStretchFactor(0, 1)  # 20%
  splitter.setStretchFactor(1, 3)  # 60%
  splitter.setStretchFactor(2, 1)  # 20%
  ```
  - File: `core/musicPlayer.py:466, 594`

- [ ] **Improve Button Grouping**
  - Issue: Buttons scattered across multiple layouts
  - Solution: Group related actions:
    - **Playlist Actions**: Load, Reload, Delete
    - **Playback Modes**: Shuffle, Loop
    - **External**: YouTube, Upload
  - File: `core/musicPlayer.py:494-516`

- [ ] **Add Visual Feedback for Actions**
  - Issue: No loading states or action confirmations
  - Solution:
    - Show spinner during YouTube upload
    - Disable buttons during operations
    - Toast notifications for actions
  - Files: `core/musicPlayer.py`

- [ ] **Consistent Spacing and Margins**
  - Issue: Inconsistent spacing (0, 9, 10px)
  - Solution: Define spacing constants:
  ```python
  SPACING_SMALL = 5
  SPACING_MEDIUM = 10
  SPACING_LARGE = 15
  MARGIN_STANDARD = 10
  ```
  - File: `core/musicPlayer.py:453-468, 602`

### Accessibility

- [ ] **Add Keyboard Shortcuts Description**
  - Issue: No documentation of available shortcuts
  - Solution: Add Help → Keyboard Shortcuts dialog
  - File: Create new dialog

- [ ] **Improve Screen Reader Support**
  - Issue: No aria labels or accessible names
  - Solution: Add `setAccessibleName()` and `setAccessibleDescription()`
  - Files: All UI components

- [ ] **Add Theme High Contrast Mode**
  - Issue: Only light/dark themes
  - Solution: Add high contrast variant for accessibility

### Progress Indication

- [ ] **Add Progress Bar for Cover Art Extraction**
  - Issue: Progress bar exists but not prominently displayed
  - Solution: Show in status bar during extraction
  - File: `core/settingManager.py:231-246`

- [ ] **Show Loading State During Playlist Loading**
  - Issue: App freezes during large playlist load
  - Solution: Show loading overlay with progress
  - File: `core/musicPlayer.py:484-488`

---

## Feature Enhancements

### Playback

- [ ] **Implement Equalizer**
  - Add 10-band equalizer with presets
  - Save EQ settings per playlist
  - Visualize frequency response

- [ ] **Add Crossfade Between Tracks**
  - Configurable fade duration (1-10 seconds)
  - Smart fade that detects silence

- [ ] **Gapless Playback**
  - Pre-load next track
  - Seamless transitions for albums

- [ ] **Replay Gain Support**
  - Read ReplayGain tags from metadata
  - Normalize volume across tracks

### Playlist Management

- [ ] **Smart Playlists**
  - Auto-generate based on criteria (genre, year, artist)
  - Dynamic updates when library changes
  ```python
  class SmartPlaylist:
      def __init__(self, name, filters):
          self.filters = filters  # e.g., {"genre": "Rock", "year": ">2000"}
      
      def generate(self, library):
          return [song for song in library if self.matches(song)]
  ```

- [ ] **Playlist Import/Export**
  - Support M3U, M3U8, PLS, XSPF formats
  - Export to Spotify/YouTube Music format

- [ ] **Collaborative Playlists**
  - Share playlists via JSON export
  - Merge playlists from multiple users

- [ ] **Recently Played / History**
  - Track play history with timestamps
  - Show most played songs/artists
  - Generate "On This Day" playlists

### Library Management

- [ ] **Automatic Music Library Scanner**
  - Watch directories for new files
  - Auto-update playlists on changes
  - Use `watchdog` library for file system events

- [ ] **Better Metadata Editing**
  - Inline editing in UI
  - Batch metadata updates
  - Fetch metadata from online databases (MusicBrainz)

- [ ] **Duplicate Detection**
  - Find duplicate files by audio fingerprint
  - Merge duplicates with same metadata

### Integration

- [ ] **Last.fm Scrobbling**
  - Track play counts
  - Sync to Last.fm profile
  - Similar artist recommendations

- [ ] **Lyrics Support**
  - Fetch lyrics from APIs (Genius, Musixmatch)
  - Display synchronized lyrics
  - Offline lyrics cache

- [ ] **Audio Visualization**
  - Spectrum analyzer
  - Waveform display
  - Customizable visualizer themes

### Export & Sharing

- [ ] **Export Listening Statistics**
  - Generate yearly/monthly reports
  - Export to CSV/JSON
  - Beautiful PDF reports

- [ ] **Podcast Support**
  - Subscribe to RSS feeds
  - Auto-download new episodes
  - Resume playback where left off

---

## Code Maintenance

### Documentation

- [ ] **Add Docstrings to All Functions**
  - Issue: Many functions lack documentation
  - Solution: Use Google-style docstrings
  ```python
  def load_playlist(self, playlist_name: str) -> List[Dict]:
      """Load a playlist by name from the playlists directory.
      
      Args:
          playlist_name: Name of the playlist without .json extension
          
      Returns:
          List of song dictionaries with metadata
          
      Raises:
          FileNotFoundError: If playlist file doesn't exist
          json.JSONDecodeError: If playlist file is corrupted
      """
  ```

- [ ] **Create Architecture Documentation**
  - Component diagram
  - Sequence diagrams for key flows:
    - Song playback flow
    - Playlist loading flow  
    - Discord integration flow
  - API documentation

- [ ] **Add Contributing Guide**
  - Code style guide (PEP 8, type hints required)
  - PR template
  - Issue templates
  - Development setup instructions

### Testing

- [ ] **Add Unit Tests**
  - Target 80%+ code coverage
  - Test critical components:
    - `PlaylistManager`
    - `ConfigManager`
    - `DiscordIntegration`
  - Use `pytest` framework

- [ ] **Add Integration Tests**
  - Test UI workflows
  - Test playlist CRUD operations
  - Test settings persistence

- [ ] **Add Performance Tests**
  - Benchmark playlist loading
  - Benchmark search performance
  - Memory leak detection

### Code Quality Tools

- [ ] **Setup Pre-commit Hooks**
  ```yaml
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/psf/black
      rev: 23.3.0
      hooks:
        - id: black
    - repo: https://github.com/PyCQA/flake8
      rev: 6.0.0
      hooks:
        - id: flake8
    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.3.0
      hooks:
        - id: mypy
  ```

- [ ] **Add CI/CD Pipeline**
  - GitHub Actions workflow
  - Run tests on PR
  - Build releases automatically
  - Deploy documentation

- [ ] **Code Coverage Reporting**
  - Integrate with Codecov or Coveralls
  - Fail PR if coverage drops

### Refactoring

- [ ] **Extract UI Stylesheet to Separate File**
  - Issue: Inline styles throughout code
  - Solution: Create `resources/styles.qss`
  - File: `core/musicPlayer.py:150, 181, etc.`

- [ ] **Migrate from `fuzzywuzzy` to `rapidfuzz`**
  - Issue: `fuzzywuzzy` is slower and unmaintained
  - Solution: Replace with `rapidfuzz` (10-50x faster)
  - File: `core/musicPlayer.py:69`, search functionality

- [ ] **Remove Unused Imports**
  - Issue: `qdarktheme` imported but may not be used
  - Solution: Run `autoflake` to remove unused imports
  - File: `main.py:30`

- [ ] **Consolidate Window Title Updates**
  - Issue: Window title set in multiple places
  - Solution: Single method for updating title
  - Files: `core/musicPlayer.py:303-304`

---

## Implementation Priority Matrix

| Priority | Category | Estimated Effort | Impact |
|----------|----------|------------------|--------|
| P0 | Thread Safety Fix | 3 days | High |
| P0 | State Machine Refactor | 5 days | High |
| P0 | Config Manager | 2 days | High |
| P1 | Code Structure Split | 10 days | High |
| P1 | Memory Cache LRU | 2 days | Medium |
| P1 | Type Hints | 5 days | Medium |
| P2 | UI Responsive Layout | 4 days | Medium |
| P2 | Testing Framework | 7 days | High |
| P3 | Feature: Equalizer | 5 days | Low |
| P3 | Feature: Smart Playlists | 4 days | Low |

---

## Quick Wins (Can Implement Today)

1. **Add type hints to `config.py`** (30 min)
2. **Extract button width constant** (15 min)
3. **Add docstring to `get_config_path()`** (10 min)
4. **Replace `fuzzywuzzy` with `rapidfuzz`** (30 min)
5. **Add config validation with Pydantic** (1 hour)
6. **Implement search debouncing** (45 min)
7. **Add LRU cache to cover art** (1 hour)
8. **Centralize version comparison** (30 min)

---

## Breaking Changes Requiring Major Version Bump

- [ ] SQLite migration for playlists (v2.0.0)
- [ ] Config file format change for validation (v2.0.0)
- [ ] API changes from code restructuring (v2.0.0)

---

## Notes

- Consider creating a roadmap document for feature additions
- Some refactorings can be done incrementally without breaking changes
- Performance optimizations should be measured before/after
- All changes should maintain backward compatibility when possible

---

**Legend:**
- 🔴 High Priority - Critical issues affecting stability/security
- 🟡 Medium Priority - Important improvements affecting performance/UX
- 🟢 Low Priority - Nice-to-have features and minor improvements
