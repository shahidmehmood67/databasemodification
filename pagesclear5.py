import os
from PIL import Image
import numpy as np

# ==== CONFIG ====
# FOLDER_PATH = r"D:\Assets\modified\pages\MODSHORT\3"
FOLDER_PATH = r"D:\Assets\modified\pages\MOD4"
IMAGE_EXTENSION = ".png"

# ==== UNCONDITIONAL AREAS ====
# AREAS_TO_CLEAR = [
#     (0,    0, 52,    60),   # Top left rows
#     (1099,    0, 1151,    60),   # Top Right rows
#
#     (0, 1986, 52, 2047),   # Bottom left rows
#     (1099, 1986, 1151, 2047),   # Bottom right rows
#     (1099, 1964, 1151, 1964),  # Bottom right row 1964
#
#     (0, 0, 552, 60),  # Top start left rows
#     (603, 0, 1151, 60),  # Top start Right rows
#
#     (0, 1988, 528, 2047),  # Bottom end left rows
#     (625, 1988, 1151, 2047),  # Bottom end right rows
# ]

AREAS_TO_CLEAR = [
    (0, 0, 548, 60),  # Top start left rows
    (613, 0, 1151, 60),  # Top start Right rows

    (0, 1988, 528, 2047),  # Bottom end left rows
    (625, 1988, 1151, 2047),  # Bottom end right rows
]

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


def black_or_transparent_mask_pixels(pixels):
    a = pixels[..., 3]
    rgb = pixels[..., :3]
    is_transparent = (a == 0)
    is_black = np.all(rgb == 0, axis=-1)
    return is_transparent | is_black


# ---------------- processing functions ----------------
def process_single_image(path):
    print(f"\nProcessing: {path}")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]

    # 1) Unconditional clears
    for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c >= x1c and y2c >= y1c:
            arr[y1c:y2c+1, x1c:x2c+1, 3] = 0
            arr[y1c:y2c+1, x1c:x2c+1, 0:3] = 0
            print(f"  [UNC] Cleared area ({x1c},{y1c})-({x2c},{y2c})")

    total_removed = 0

    Image.fromarray(arr).save(path, format="PNG", optimize=True, compress_level=9)
    print(f"  ✅ Saved (removed approx. {total_removed} pixels).")


# ---------------- main ----------------
def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print("FOLDER_PATH must be an existing directory.")
        return
    files = sorted(os.listdir(folder_path))
    pngs = [f for f in files if f.lower().endswith(IMAGE_EXTENSION)]
    if not pngs:
        print("No PNG files found in folder.")
        return
    for fname in pngs:
        full = os.path.join(folder_path, fname)
        try:
            process_single_image(full)
        except Exception as e:
            print(f"Error processing {fname}: {e}")


if __name__ == "__main__":
    process_folder(FOLDER_PATH)
