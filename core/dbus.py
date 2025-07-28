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

# ruff: noqa
# type: ignore
# core/dbus.py
# =============
# D-Bus Interface for MPRIS:
#
# This module implements the MPRIS (Media Player Remote Interfacing Specification) D-Bus interface
# for IotaPlayer using dbus-next. It exposes player metadata (title, artist, album, cover art, etc.)
# and playback status to Linux desktop environments and compatible widgets.
#
# The implementation is read-only: playback controls (play, pause, next, etc.) are disabled,
# and only metadata and status are provided. This ensures maximum compatibility and stability
# with desktop integrations such as playerctl, KDE Plasma, GNOME Shell, and Waybar.
#
# The MPRIS service is started asynchronously and updates metadata in real time as songs change.
# =============

import logging
import asyncio
from dbus_next.aio import MessageBus
from dbus_next.service import (ServiceInterface, method, dbus_property, PropertyAccess)
from dbus_next import Variant

MPRIS_BUS_NAME = 'org.mpris.MediaPlayer2.IotaPlayer'
MPRIS_OBJECT_PATH = '/org/mpris/MediaPlayer2'

class MPRISRootInterface(ServiceInterface):
    def __init__(self, player):
        super().__init__('org.mpris.MediaPlayer2')
        self.player = player

    @method()
    def Raise(self):
        logging.info('MPRIS: Raise called')

    @method()
    def Quit(self):
        logging.info('MPRIS: Quit called')

    @dbus_property(PropertyAccess.READ)
    def CanQuit(self) -> 'b': 
        return False

    @dbus_property(PropertyAccess.READ)
    def CanRaise(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def HasTrackList(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def Identity(self) -> 's':
        return 'IotaPlayer'

    @dbus_property(PropertyAccess.READ)
    def DesktopEntry(self) -> 's':
        return 'iotaplayer'

    @dbus_property(PropertyAccess.READ)
    def SupportedUriSchemes(self) -> 'as':
        return ['file']

    @dbus_property(PropertyAccess.READ)
    def SupportedMimeTypes(self) -> 'as':
        return ['audio/mpeg', 'audio/mp3', 'audio/x-wav', 'audio/flac']

class MPRISPlayerInterface(ServiceInterface):
    def __init__(self, player):
        super().__init__('org.mpris.MediaPlayer2.Player')
        self.player = player

    @dbus_property(PropertyAccess.READ)
    def PlaybackStatus(self) -> 's':
        if getattr(self.player, 'is_playing', False):
            return 'Playing'
        elif getattr(self.player, 'is_paused', False):
            return 'Paused'
        else:
            return 'Stopped'

    @dbus_property(PropertyAccess.READ)
    def LoopStatus(self) -> 's':
        return 'None'

    @dbus_property(PropertyAccess.READ)
    def Rate(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def Shuffle(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def Volume(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def Position(self) -> 'x':
        return int(getattr(self.player, 'current_position', 0) * 1_000_000)

    @dbus_property(PropertyAccess.READ)
    def MinimumRate(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def MaximumRate(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def CanGoNext(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanGoPrevious(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanPlay(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanPause(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanSeek(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanControl(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def Metadata(self) -> 'a{sv}':
        try:
            import os
            song = getattr(self.player, 'current_song', None) or {}
            title = song.get('title', 'Nothing is playing')
            artist = [song.get('artist', 'Unknown Artist')]
            album = song.get('album', 'Unknown Album')
            length = int(getattr(self.player, 'song_duration', 0) * 1_000_000)
            # Prefer picture_link if it's a valid URL, else use picture_path as file://
            art_url = song.get('picture_link', '')
            if not art_url:
                picture_path = song.get('picture_path', '')
                if picture_path:
                    art_url = 'file://' + os.path.abspath(picture_path)
            elif not (art_url.startswith('http://') or art_url.startswith('https://') or art_url.startswith('file://')):
                # If picture_link is a local path, convert to file://
                art_url = 'file://' + os.path.abspath(art_url)
            trackid = '/org/mpris/MediaPlayer2/track/1'
            return {
                'mpris:trackid': Variant('o', trackid),
                'xesam:title': Variant('s', title),
                'xesam:artist': Variant('as', artist),
                'xesam:album': Variant('s', album),
                'mpris:length': Variant('x', length),
                'mpris:artUrl': Variant('s', art_url),
            }
        except Exception as e:
            logging.error(f'MPRIS: Metadata error: {e}')
            return {
                'mpris:trackid': Variant('o', '/org/mpris/MediaPlayer2/track/0'),
                'xesam:title': Variant('s', 'Nothing is playing'),
                'xesam:artist': Variant('as', ['Unknown Artist']),
                'xesam:album': Variant('s', 'Unknown Album'),
                'mpris:length': Variant('x', 0),
            }
    def update_metadata(self):
        self.emit_properties_changed({'Metadata': self.Metadata})

async def run_mpris(player):
    bus = await MessageBus().connect()
    root_iface = MPRISRootInterface(player)
    player_iface = MPRISPlayerInterface(player)
    bus.export(MPRIS_OBJECT_PATH, root_iface)
    bus.export(MPRIS_OBJECT_PATH, player_iface)
    await bus.request_name(MPRIS_BUS_NAME)
    # Attach the player_iface to the player for metadata updates
    player.mpris_player_iface = player_iface
    logging.info(f"MPRIS: Service published on D-Bus (dbus-next) as {MPRIS_BUS_NAME}")
    await asyncio.get_event_loop().create_future()  # Run forever
