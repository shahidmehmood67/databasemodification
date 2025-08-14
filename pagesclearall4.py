import os
from PIL import Image
import numpy as np

# ==== CONFIG - set your folder path and thresholds here ====
# FOLDER_PATH = r"D:\Assets\modified\pages\MOD"   # folder containing PNGs to update in-place
FOLDER_PATH = r"D:\Assets\modified\pages\MOD2"
IMAGE_EXTENSION = ".png"

# thresholds (set as fraction, e.g. 0.85 == 85%)
VERTICAL_THRESHOLD = 0.65   # rows in left/right strips removed if >= this ratio of black/transparent
HORIZONTAL_THRESHOLD = 0.70 # columns in top/bottom chunks removed if >= this ratio

# ==== UNCONDITIONAL AREAS (kept exactly as you specified) ====
AREAS_TO_CLEAR = [
    (0,    0, 1151,    3),   # Top 3 rows (y=0..2)
    (0, 2043, 1151, 2047),   # Bottom last 5 rows (y=2043..2047)
    (0,    0,    2, 2047),   # First 3 columns (x=0..2)
    (1149, 0, 1151, 2047),   # Last 3 columns  (x=1149..1151)
]

# ==== CONDITIONAL STRIPS / CHUNKS ====
VERTICAL_STRIPS = [
    (0, 4, 52, 2042),        # Left vertical strip (x1,y1,x2,y2)
    (1099, 4, 1151, 2042),   # Right vertical strip
]

HORIZONTAL_CHUNKS = [
    (0,    4,  1151,  59),   # Top chunk (x1,y1,x2,y2)
    (0, 1988,  1151, 2042),  # Bottom chunk
]


# ---------------- helpers ----------------
def clamp_rect(x1, y1, x2, y2, w, h):
    """Return inclusive clamped rectangle coordinates (x1,y1,x2,y2)."""
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2

def black_or_transparent_mask_pixels(pixels):
    """
    pixels: (N,4) or (H,W,4) uint8 array
    returns boolean mask where True means "black (RGB==0) or transparent (A==0)".
    We treat any fully transparent pixel as blank, and any pure-black pixel as blank.
    """
    a = pixels[..., 3]
    rgb = pixels[..., :3]
    is_transparent = (a == 0)
    is_black = np.all(rgb == 0, axis=-1)
    return is_transparent | is_black

# ---------------- processing functions ----------------
def process_single_image(path):
    print(f"\nProcessing: {path}")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)   # shape (H, W, 4)
    h, w = arr.shape[:2]

    # 1) Unconditional clears
    for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c >= x1c and y2c >= y1c:
            arr[y1c:y2c+1, x1c:x2c+1, 3] = 0
            arr[y1c:y2c+1, x1c:x2c+1, 0:3] = 0
            print(f"  [UNC] Cleared area ({x1c},{y1c})-({x2c},{y2c})")

    total_removed = 0

    # 2) Vertical strips: row-by-row
    for (x1, y1, x2, y2) in VERTICAL_STRIPS:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c < x1c or y2c < y1c:
            continue
        width = x2c - x1c + 1
        print(f"  [VERT STRIP] checking ({x1c},{y1c})-({x2c},{y2c}) rows {y1c}..{y2c}")

        for y in range(y1c, y2c+1):
            row = arr[y, x1c:x2c+1]  # shape (width,4)
            mask = black_or_transparent_mask_pixels(row)  # (width,)
            ratio = float(mask.sum()) / width if width > 0 else 0.0
            # log
            print(f"    Row {y}: black/transparent = {ratio:.2%}", end="")
            if ratio <= VERTICAL_THRESHOLD:
                arr[y, x1c:x2c+1, 3] = 0
                arr[y, x1c:x2c+1, 0:3] = 0
                total_removed += int(mask.size)
                print("  -> REMOVED")
            else:
                print("  -> kept")

    # 3) Horizontal chunks: column-by-column within each chunk
    for (x1, y1, x2, y2) in HORIZONTAL_CHUNKS:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c < x1c or y2c < y1c:
            continue
        height = y2c - y1c + 1
        print(f"  [HORIZ CHUNK] checking ({x1c},{y1c})-({x2c},{y2c}) cols {x1c}..{x2c}")

        for x in range(x1c, x2c+1):
            col = arr[y1c:y2c+1, x]  # shape (height,4)
            mask = black_or_transparent_mask_pixels(col)  # (height,)
            ratio = float(mask.sum()) / height if height > 0 else 0.0
            # log
            print(f"    Col {x}: black/transparent = {ratio:.2%}", end="")
            if ratio <= HORIZONTAL_THRESHOLD:
                arr[y1c:y2c+1, x, 3] = 0
                arr[y1c:y2c+1, x, 0:3] = 0
                total_removed += int(mask.size)
                print("  -> REMOVED")
            else:
                print("  -> kept")

    # 4) Save in-place (lossless)
    Image.fromarray(arr).save(path, format="PNG", optimize=True, compress_level=9)
    print(f"  ✅ Saved (removed approx. {total_removed} pixels).")


# ---------------- main ----------------
def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print("FOLDER_PATH must be an existing directory.")
        return
    files = sorted(os.listdir(folder_path))
    pngs = [f for f in files if f.lower().endswith(IMAGE_EXTENSION := ".png")]
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
