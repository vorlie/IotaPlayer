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

# core/mprisThread.py
# =============
# This module implements the MPRIS (Media Player Remote Interfacing Specification)
# D-Bus interface for IotaPlayer using dbus-next.
# It runs in a separate QThread to avoid blocking the main GUI thread.
# =============
import logging
import asyncio
from core.dbus import run_mpris
from PyQt6.QtCore import QThread


class MPRISServiceThread(QThread):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_mpris(self.player))
        except Exception as e:
            logging.error(f"MPRIS: Exception in dbus-next QThread: {e}")
        finally:
            loop.close()

_mpris_thread = None

def start_mpris(player):
    global _mpris_thread
    if _mpris_thread is not None:
        logging.info("MPRIS: Already running (dbus-next)")
        return
    _mpris_thread = MPRISServiceThread(player)
    _mpris_thread.start()
    logging.info("MPRIS: dbus-next QThread started.")
