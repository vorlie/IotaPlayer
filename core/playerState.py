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

# core/playerState.py
# =============
# Player state management using enum-based state machine.
# Replaces multiple boolean flags (is_playing, is_paused, has_started)
# with a single, validated state variable.
# =============

from enum import Enum, auto
from typing import Set, Dict
import logging


class PlayerState(Enum):
    """
    Enumeration of all possible player states.
    
    State Descriptions:
        STOPPED: No song loaded or playback explicitly stopped
        LOADING: Song is being loaded from disk
        READY: Song loaded and ready to play, but not yet started
        PLAYING: Song is currently playing
        PAUSED: Playback temporarily paused
        BUFFERING: Waiting for data (for future streaming support)
        ERROR: An error occurred during playback
    """
    STOPPED = auto()
    LOADING = auto()
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    BUFFERING = auto()
    ERROR = auto()


# Valid state transitions
# Dict[PlayerState, Set[PlayerState]]: maps each state to its possible next states
VALID_TRANSITIONS: Dict[PlayerState, Set[PlayerState]] = {
    PlayerState.STOPPED: {
        PlayerState.LOADING,  # User selects a song
        PlayerState.ERROR,     # Error during init
    },
    PlayerState.LOADING: {
        PlayerState.READY,     # Song loaded successfully
        PlayerState.ERROR,     # Load failed
        PlayerState.STOPPED,   # User cancels
    },
    PlayerState.READY: {
        PlayerState.PLAYING,   # User presses play
        PlayerState.STOPPED,   # User stops/changes song
        PlayerState.LOADING,   # User loads different song
        PlayerState.ERROR,     # Error during preparation
    },
    PlayerState.PLAYING: {
        PlayerState.PAUSED,    # User pauses
        PlayerState.STOPPED,   # User stops or song ends
        PlayerState.BUFFERING, # Waiting for data (future)
        PlayerState.ERROR,     # Playback error
        PlayerState.READY,     # Seeking/position change
    },
    PlayerState.PAUSED: {
        PlayerState.PLAYING,   # User resumes
        PlayerState.STOPPED,   # User stops
        PlayerState.READY,     # Seeking while paused
        PlayerState.ERROR,     # Error during pause
    },
    PlayerState.BUFFERING: {
        PlayerState.PLAYING,   # Buffer filled, resume
        PlayerState.ERROR,     # Buffering failed
        PlayerState.STOPPED,   # User stops
    },
    PlayerState.ERROR: {
        PlayerState.STOPPED,   # Reset after error
        PlayerState.LOADING,   # Retry loading
    },
}


class PlayerStateMachine:
    """
    Manages player state transitions with validation.
    
    Ensures only valid state transitions occur and provides logging
    for debugging state-related issues.
    
    Usage:
        state_machine = PlayerStateMachine()
        state_machine.transition_to(PlayerState.PLAYING)
        current = state_machine.current_state
    """
    
    def __init__(self, initial_state: PlayerState = PlayerState.STOPPED):
        """
        Initialize the state machine.
        
        Args:
            initial_state: Starting state (default: STOPPED)
        """
        self._current_state = initial_state
        self._logger = logging.getLogger(__name__)
        self._logger.info(f"PlayerStateMachine initialized in {initial_state.name} state")
    
    @property
    def current_state(self) -> PlayerState:
        """Get the current player state."""
        return self._current_state
    
    def can_transition_to(self, new_state: PlayerState) -> bool:
        """
        Check if transition to new state is valid.
        
        Args:
            new_state: State to transition to
            
        Returns:
            bool: True if transition is allowed
        """
        return new_state in VALID_TRANSITIONS.get(self._current_state, set())
    
    def transition_to(self, new_state: PlayerState, force: bool = False) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: State to transition to
            force: If True, skip validation (use with caution)
            
        Returns:
            bool: True if transition succeeded
            
        Raises:
            ValueError: If transition is invalid and force=False
        """
        if self._current_state == new_state:
            self._logger.debug(f"Already in {new_state.name} state, no transition needed")
            return True
        
        if not force and not self.can_transition_to(new_state):
            error_msg = (
                f"Invalid state transition: {self._current_state.name} -> {new_state.name}. "
                f"Valid transitions from {self._current_state.name}: "
                f"{[s.name for s in VALID_TRANSITIONS.get(self._current_state, set())]}"
            )
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        
        old_state = self._current_state
        self._current_state = new_state
        
        log_msg = f"State transition: {old_state.name} -> {new_state.name}"
        if force:
            log_msg += " (forced)"
        self._logger.info(log_msg)
        
        return True
    
    def is_stopped(self) -> bool:
        """Check if player is stopped."""
        return self._current_state == PlayerState.STOPPED
    
    def is_playing(self) -> bool:
        """Check if player is actively playing."""
        return self._current_state == PlayerState.PLAYING
    
    def is_paused(self) -> bool:
        """Check if player is paused."""
        return self._current_state == PlayerState.PAUSED
    
    def is_ready(self) -> bool:
        """Check if player has a song loaded and ready."""
        return self._current_state == PlayerState.READY
    
    def is_loading(self) -> bool:
        """Check if player is loading a song."""
        return self._current_state == PlayerState.LOADING
    
    def is_in_error_state(self) -> bool:
        """Check if player is in error state."""
        return self._current_state == PlayerState.ERROR
    
    def can_play(self) -> bool:
        """Check if play action is currently valid."""
        return self._current_state in {PlayerState.READY, PlayerState.PAUSED}
    
    def can_pause(self) -> bool:
        """Check if pause action is currently valid."""
        return self._current_state == PlayerState.PLAYING
    
    def can_stop(self) -> bool:
        """Check if stop action is currently valid."""
        return self._current_state in {
            PlayerState.PLAYING,
            PlayerState.PAUSED,
            PlayerState.READY,
            PlayerState.BUFFERING
        }
    
    def reset(self) -> None:
        """Reset state machine to STOPPED state."""
        self._logger.info(f"Resetting state machine from {self._current_state.name} to STOPPED")
        self._current_state = PlayerState.STOPPED
