from PyQt5.QtCore import QThread, pyqtSignal
from mutagen import File
from mutagen.id3 import APIC
from mutagen.flac import Picture
import os

class CoverArtExtractor(QThread):
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal()

    def __init__(self, music_dirs, cache, size=250, parent=None):
        super().__init__(parent)
        self.music_dirs = music_dirs  # List of directories to scan
        self.cache = cache            # Instance of CoverArtCache
        self.size = size

    def run(self):
        files = []
        for music_dir in self.music_dirs:
            for root, _, filenames in os.walk(music_dir):
                for f in filenames:
                    if f.lower().endswith(('.mp3', '.flac', '.ogg', '.m4a')):
                        files.append(os.path.join(root, f))
        total = len(files)
        for idx, path in enumerate(files, 1):
            # --- Skip if cover already cached ---
            cache_key = f"{os.path.basename(path)}_{self.size}"
            cache_file = os.path.join(self.cache.cache_dir, cache_key + ".png")
            if os.path.exists(cache_file):
                self.progress.emit(idx, total)
                continue
            cover = self.extract_cover(path)
            if cover:
                self.cache.save_cover_from_bytes(path, cover, self.size)
            self.progress.emit(idx, total)
        self.finished.emit()

    def extract_cover(self, filepath):
        try:
            audio = File(filepath)
            if audio is None:
                return None
            # MP3
            if filepath.lower().endswith('.mp3') and audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        return tag.data
            # FLAC
            if filepath.lower().endswith('.flac') and hasattr(audio, 'pictures'):
                for pic in audio.pictures:
                    if isinstance(pic, Picture):
                        return pic.data
            # M4A/MP4
            if filepath.lower().endswith('.m4a') and 'covr' in audio:
                return audio['covr'][0]
            # OGG
            if filepath.lower().endswith('.ogg') and hasattr(audio, 'pictures'):
                for pic in audio.pictures:
                    return pic.data
        except Exception as e:
            print(f"Error extracting cover from {filepath}: {e}")
        return None