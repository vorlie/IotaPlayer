import os
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
import io

class CoverArtCache:
    def __init__(self, cache_dir="cover_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache = {}

    def get_cover(self, image_path, size=250):
        cache_key = f"{os.path.basename(image_path)}_{size}"
        cache_file = os.path.join(self.cache_dir, cache_key + ".png")
        if cache_key in self.cache:
            return self.cache[cache_key]
        if os.path.exists(cache_file):
            pixmap = QPixmap(cache_file)
            self.cache[cache_key] = pixmap
            return pixmap
        pixmap = self.process_and_cache(image_path, cache_file, size)
        self.cache[cache_key] = pixmap
        return pixmap

    def process_and_cache(self, image_path, cache_file, size):
        try:
            img = Image.open(image_path).convert("RGBA")
            w, h = img.size
            # Crop to center square
            if w != h:
                min_side = min(w, h)
                left = (w - min_side) // 2
                top = (h - min_side) // 2
                img = img.crop((left, top, left + min_side, top + min_side))
            img = img.resize((size, size), Image.LANCZOS)
            img.save(cache_file)
            return QPixmap.fromImage(ImageQt.ImageQt(img))
        except Exception as e:
            print(f"Error processing cover art: {e}")
            return QPixmap("default.png")

    def save_cover_from_bytes(self, song_path, img_bytes, size):
        cache_key = f"{os.path.basename(song_path)}_{size}"
        cache_file = os.path.join(self.cache_dir, cache_key + ".png")
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            w, h = img.size
            # Crop to center square
            if w != h:
                min_side = min(w, h)
                left = (w - min_side) // 2
                top = (h - min_side) // 2
                img = img.crop((left, top, left + min_side, top + min_side))
            img = img.resize((size, size), Image.LANCZOS)
            img.save(cache_file)
        except Exception as e:
            print(f"Error saving cover art: {e}")