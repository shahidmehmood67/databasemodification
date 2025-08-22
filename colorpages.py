import os
from PIL import Image
import numpy as np

# ==== CONFIG ====
FOLDER_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\Pages\MOD1"
IMAGE_EXTENSION = ".png"

# Areas to color: list of (x1, y1, x2, y2)
AREAS_TO_COLOR = [
    (53, 60, 1098, 64),  # top
    (53, 1979, 1098, 1983),  # bottom

    (53, 60, 57, 1983),  # left
    (1094, 60, 1098, 1983),  # right
]

# Color in RGBA (red, green, blue, alpha)
FILL_COLOR = (0, 0, 0, 255)  # Solid Black


# ---------------- helpers ----------------
def clamp_rect(x1, y1, x2, y2, w, h):
    """Return inclusive clamped rectangle coordinates."""
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2


# ---------------- processing ----------------
def process_single_image(path, rects, color):
    print(f"\n🎨 Coloring {os.path.basename(path)}")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]

    for (x1, y1, x2, y2) in rects:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        arr[y1c:y2c+1, x1c:x2c+1] = color
        print(f"   ✅ Applied color {color} to ({x1c},{y1c})-({x2c},{y2c})")

    Image.fromarray(arr).save(path, format="PNG", optimize=True, compress_level=9)
    print(f"   💾 Saved {os.path.basename(path)}")


def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print("❌ FOLDER_PATH must be an existing directory.")
        return

    files = sorted(os.listdir(folder_path))
    pngs = [f for f in files if f.lower().endswith(IMAGE_EXTENSION)]
    if not pngs:
        print("⚠️ No PNG files found in folder.")
        return

    for fname in pngs:
        full_path = os.path.join(folder_path, fname)
        try:
            process_single_image(full_path, AREAS_TO_COLOR, FILL_COLOR)
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")


if __name__ == "__main__":
    process_folder(FOLDER_PATH)
