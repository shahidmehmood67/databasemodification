from PIL import Image
import numpy as np
import os
import shutil
import subprocess

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page004.png"
RUN_OPTIPNG = False                 # set True if you want to run optipng after saving
OPTIPNG_ARGS = ["-o7", "-quiet"]    # lossless compression; no chunk stripping (keeps metadata)
MATCH_ALPHA = True                  # if False, match only RGB (useful if some pixels aren't fully 255 alpha)

# Colors to remove (exact matches)
TARGET_COLORS_RGBA = np.array([
    [162, 156, 118, 255],  # #a29c76
    [204, 204, 153, 255],  # #cccc99
    [102,  51,  51, 255],  # #663333
    [234, 234, 234, 255],  # #eaeaea
], dtype=np.uint8)
# ==== AREAS ====
# All rectangles to clear unconditionally: (x1, y1, x2, y2) inclusive
# NOTE: Top 3 rows must be y=0..2 inclusive. (Your original had 3 which wipes 4 rows.)
AREAS_TO_CLEAR = [
    (0, 0, 1151, 2),         # Top 3 rows (y = 0..2)
    (0, 2043, 1151, 2047),   # Bottom last 5 rows (y = 2043..2047)
    (0, 0, 2, 2047),         # First 3 columns (x = 0..2)
    (1149, 0, 1151, 2047),   # Last 3 columns (x = 1149..1151)

    # Top-left chunk strips (1px tall lines, y = 4..59)
    *[(0, y, 552, y) for y in range(4, 60)],

    # Top-right chunk strips (1px tall lines, y = 4..59)
    *[(603, y, 1151, y) for y in range(4, 60)],

    # Bottom-left chunk strips (1px tall lines, y = 1988..2042)
    *[(0, y, 528, y) for y in range(1988, 2043)],

    # Bottom-right chunk strips (1px tall lines, y = 1988..2042)
    *[(627, y, 1151, y) for y in range(1988, 2043)],
]

# Rectangles where we clear ONLY if pixel matches one of TARGET_COLORS_RGBA
COLOR_FILTERED_STRIPS = [
    (0, 60, 52, 1987),        # Left vertical strip
    (1099, 60, 1151, 1987),   # Right vertical strip
]

def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

def clamp_rect(x1, y1, x2, y2, w, h):
    # Ensure x1<=x2, y1<=y2 and clamp inside image bounds (inclusive coords)
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2

def clear_region(arr, x1, y1, x2, y2):
    """Unconditionally make region transparent (alpha=0) and RGB=0."""
    region = arr[y1:y2+1, x1:x2+1]
    region[..., 3] = 0         # alpha -> transparent
    region[..., 0:3] = 0       # RGB -> black (invisible when alpha=0)

def clear_region_by_colors(arr, x1, y1, x2, y2, colors_rgba, match_alpha=True):
    """Make pixels transparent only if they match one of the given colors."""
    region = arr[y1:y2+1, x1:x2+1]  # view into arr
    # Build a boolean mask where any of the target colors match
    if match_alpha:
        mask = np.zeros(region.shape[:2], dtype=bool)
        for c in colors_rgba:
            # Compare all 4 channels
            mask |= np.all(region == c, axis=-1)
    else:
        mask = np.zeros(region.shape[:2], dtype=bool)
        for c in colors_rgba:
            # Compare only RGB
            mask |= np.all(region[..., :3] == c[:3], axis=-1)

    # Apply transparency only where mask is True
    region[mask, 3] = 0
    region[mask, 0:3] = 0

# 1) Load image as RGBA
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)  # shape: (h, w, 4) with dtype=uint8
h, w = arr.shape[:2]

# 2) Unconditional clears
for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
    x1, y1, x2, y2 = clamp_rect(x1, y1, x2, y2, w, h)
    if x2 >= x1 and y2 >= y1:
        clear_region(arr, x1, y1, x2, y2)

# 3) Color-filtered clears (only remove the specified colors within these strips)
for (x1, y1, x2, y2) in COLOR_FILTERED_STRIPS:
    x1, y1, x2, y2 = clamp_rect(x1, y1, x2, y2, w, h)
    if x2 >= x1 and y2 >= y1:
        clear_region_by_colors(arr, x1, y1, x2, y2, TARGET_COLORS_RGBA, match_alpha=MATCH_ALPHA)

# 4) Save (lossless) with Pillow; let Pillow infer mode (avoids deprecation warning)
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)

# 5) Optional: run optipng (lossless recompression)
if RUN_OPTIPNG:
    optipng_path = shutil.which("optipng")
    if optipng_path:
        try:
            subprocess.run([optipng_path, *OPTIPNG_ARGS, IMAGE_PATH], check=True)
            after = os.path.getsize(IMAGE_PATH)
            print(f"✅ OptiPNG: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
        except subprocess.CalledProcessError:
            after = os.path.getsize(IMAGE_PATH)
            print(f"⚠️ OptiPNG error (kept Pillow output). Size: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
    else:
        after = os.path.getsize(IMAGE_PATH)
        print(f"ℹ️ optipng not found on PATH. Pillow only: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
else:
    after = os.path.getsize(IMAGE_PATH)
    print(f"ℹ️ Skipped OptiPNG. Size: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
