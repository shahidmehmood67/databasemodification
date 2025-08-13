from PIL import Image
import numpy as np
import os


# ==== CONFIG ====
# IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
IMAGE_PATH = r"D:\Assets\modified\pages\MOD\page005.png"

# Target RGBA colors to remove inside strips (exact matches)
TARGET_COLORS_RGBA = np.array([
    [161, 156, 118,255],  # #a19c76
    [162, 156, 118, 255],  # #a29c76
    [204, 204, 153, 255],  # #cccc99
    [102,  51,  51, 255],  # #663333
    [234, 234, 234, 255],  # #eaeaea
    [0, 0, 0, 255],  # #000000 black
], dtype=np.uint8)

#a19c76
# Unconditional areas (keeps your prior config)
AREAS_TO_CLEAR = [
    (0, 0, 1151, 2),         # Top 3 rows (y = 0..2)
    (0, 2043, 1151, 2047),   # Bottom last 5 rows (y = 2043..2047)
    (0, 0, 2, 2047),         # First 3 columns
    (1149, 0, 1151, 2047),   # Last 3 columns

    # Top-left chunk strips (1px rows)
    *[(0, y, 552, y) for y in range(4, 60)],
    # Top-right chunk strips (1px rows)
    *[(603, y, 1151, y) for y in range(4, 60)],
    # Bottom-left chunk strips (1px rows)
    *[(0, y, 528, y) for y in range(1988, 2043)],
    # Bottom-right chunk strips (1px tall)
    *[(627, y, 1151, y) for y in range(1988, 2043)],
]

# Vertical strips where removal is conditional and controlled by blank-row toggling:
COLOR_FILTERED_STRIPS = [
    (0, 60, 52, 1987),        # Left vertical strip (inclusive coords)
    (1099, 60, 1151, 1987),   # Right vertical strip
]

# Behavior tuning
BLANK_ROW_THRESHOLD = 2   # consecutive blank rows required to toggle pause/remove
# ------------------------------- helpers -----------------------------------

def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

def clamp_rect(x1, y1, x2, y2, w, h):
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2

def clear_region(arr, x1, y1, x2, y2):
    """Unconditionally set region alpha=0 and RGB=0 (transparent)."""
    arr[y1:y2+1, x1:x2+1, 3] = 0
    arr[y1:y2+1, x1:x2+1, 0:3] = 0

# ------------------------------- main --------------------------------------
# Load image
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)  # uint8 (h, w, 4)
h, w = arr.shape[:2]
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
print(f"Loaded {IMAGE_PATH} ({w}x{h}) size_before={bytes_to_kb(before)}")

# 1) Apply unconditional clears (top/bottom rows, first/last columns, chunk strips)
for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
    x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
    if x2c >= x1c and y2c >= y1c:
        clear_region(arr, x1c, y1c, x2c, y2c)

# 2) Process left/right strips


# 3) Save (Pillow)
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
after = os.path.getsize(IMAGE_PATH)
print(f"Saved (Pillow): {bytes_to_kb(before)} -> {bytes_to_kb(after)} ")


