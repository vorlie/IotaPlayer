import logging
import asyncio
from core.dbus import run_mpris
from PyQt5.QtCore import QThread


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
