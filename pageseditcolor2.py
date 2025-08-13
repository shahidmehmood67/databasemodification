from PIL import Image
import numpy as np
import os
import shutil
import subprocess

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
RUN_OPTIPNG = False                 # True to run optipng after save (must be on PATH)
OPTIPNG_ARGS = ["-o7", "-quiet"]    # lossless recompression
MATCH_ALPHA = True                  # when matching target colors: require alpha match if True

# Colors to remove (exact RGBA matches)
TARGET_COLORS_RGBA = np.array([
    [162, 156, 118, 255],  # #a29c76
    [204, 204, 153, 255],  # #cccc99
    [102,  51,  51, 255],  # #663333
    [234, 234, 234, 255],  # #eaeaea
    [0,     0,   0, 255],  # #000000 black
], dtype=np.uint8)

# ==== AREAS ====
# Unconditional rectangles to clear fully (x1,y1,x2,y2 inclusive)
AREAS_TO_CLEAR = [
    (0, 0, 1151, 2),         # Top 3 rows (y = 0..2)
    (0, 2043, 1151, 2047),   # Bottom last 5 rows (y = 2043..2047)
    (0, 0, 2, 2047),         # First 3 columns (x = 0..2)
    (1149, 0, 1151, 2047),   # Last 3 columns (x = 1149..1151)

    # Top-left chunk strips (1px rows)
    *[(0, y, 552, y) for y in range(4, 60)],
    # Top-right chunk strips
    *[(603, y, 1151, y) for y in range(4, 60)],
    # Bottom-left chunk strips (1px rows)
    *[(0, y, 528, y) for y in range(1988, 2043)],
    # Bottom-right chunk strips (1px rows)
    *[(627, y, 1151, y) for y in range(1988, 2043)],
]

# Vertical strips where removal must be color-filtered (not unconditional)
COLOR_FILTERED_STRIPS = [
    (0, 60, 52, 1987),        # Left vertical strip
    (1099, 60, 1151, 1987),   # Right vertical strip
]

# Detection parameters (tweak if needed)
DARK_LUMINANCE_THRESHOLD = 120.0   # luminance <= this considered "dark" (text)
DARK_PIXEL_ROW_MIN = 1             # min dark pixels in a row to consider it part of text
TEXT_BLOCK_MARGIN = 3              # expand detected text block by these many rows on both sides

# ---------------------------------------------------------
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
    """Unconditionally make region transparent (alpha=0) and RGB=0."""
    region = arr[y1:y2+1, x1:x2+1]
    region[..., 3] = 0
    region[..., 0:3] = 0

def clear_region_by_exact_colors(arr, x1, y1, x2, y2, target_colors_rgba, match_alpha=True):
    """
    Make pixels transparent only if they exactly match one of target_colors_rgba.
    target_colors_rgba: array of shape (n,4) dtype uint8
    """
    region = arr[y1:y2+1, x1:x2+1]
    mask = np.zeros(region.shape[:2], dtype=bool)
    if match_alpha:
        for c in target_colors_rgba:
            mask |= np.all(region == c, axis=-1)
    else:
        for c in target_colors_rgba:
            mask |= np.all(region[..., :3] == c[:3], axis=-1)
    if mask.any():
        region[mask, 3] = 0
        region[mask, 0:3] = 0

def detect_text_block_in_strip(arr_rgb_alpha, x1, y1, x2, y2, target_colors_rgb):
    """
    Return (start_y, end_y) inclusive of the largest contiguous run of rows that look like text.
    Detection scans rows inside the rectangle and counts 'dark' pixels excluding target border colors.
    If no dark rows found -> returns None.
    """
    region = arr_rgb_alpha[y1:y2+1, x1:x2+1]                # shape (H, W, 4)
    H, W = region.shape[:2]

    # Build mask of nontransparent pixels
    alpha = region[..., 3]
    nontrans_mask = alpha > 0

    # Build mask of pixels that equal any target border RGB (ignore alpha here)
    target_mask = np.zeros((H, W), dtype=bool)
    for c_rgb in target_colors_rgb:
        target_mask |= np.all(region[..., :3] == c_rgb, axis=-1)

    # Compute luminance for candidate dark pixels
    rgb = region[..., :3].astype(np.float32)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    # A dark text-candidate pixel: non-transparent, not a border target color, and dark luminance
    dark_pixel_mask = nontrans_mask & (~target_mask) & (lum <= DARK_LUMINANCE_THRESHOLD)

    # Count dark pixels per row
    dark_counts = np.count_nonzero(dark_pixel_mask, axis=1)  # length H

    # Rows that qualify as "text rows"
    text_row_indices = np.where(dark_counts >= DARK_PIXEL_ROW_MIN)[0]  # relative indices 0..H-1

    if text_row_indices.size == 0:
        return None  # no text detected

    # Find largest contiguous group of rows (to avoid stray single-row noise)
    splits = np.split(text_row_indices, np.where(np.diff(text_row_indices) != 1)[0] + 1)
    longest = max(splits, key=lambda g: g.size)
    rel_start, rel_end = int(longest[0]), int(longest[-1])
    # convert to absolute image coordinates and expand by margin
    start_y = max(y1, y1 + rel_start - TEXT_BLOCK_MARGIN)
    end_y   = min(y2,   y1 + rel_end   + TEXT_BLOCK_MARGIN)
    return start_y, end_y

# ---------------- main ----------------
# 1) Load original image (preserve original for detection)
img = Image.open(IMAGE_PATH).convert("RGBA")
arr_orig = np.array(img)   # original for detection
arr = arr_orig.copy()      # this will be modified and saved
h, w = arr.shape[:2]

print(f"Image: {w}x{h}  size_before = {bytes_to_kb(os.path.getsize(IMAGE_PATH)) if os.path.exists(IMAGE_PATH) else 'N/A'}")

# 2) Detect text regions inside each vertical strip (using original image)
target_rgb_only = TARGET_COLORS_RGBA[:, :3]
strip_text_ranges = {}  # map (x1,y1,x2,y2) -> (start_y,end_y) or None

for (sx1, sy1, sx2, sy2) in COLOR_FILTERED_STRIPS:
    sx1c, sy1c, sx2c, sy2c = clamp_rect(sx1, sy1, sx2, sy2, w, h)
    tr = detect_text_block_in_strip(arr_orig, sx1c, sy1c, sx2c, sy2c, target_rgb_only)
    strip_text_ranges[(sx1c, sy1c, sx2c, sy2c)] = tr
    if tr is None:
        print(f"Strip {(sx1c, sy1c, sx2c, sy2c)}: NO text detected -> will remove target colors across entire strip.")
    else:
        print(f"Strip {(sx1c, sy1c, sx2c, sy2c)}: detected text block rows {tr[0]}..{tr[1]} (kept)")

# 3) Apply unconditional clears first (these are absolute)
for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
    x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
    if x2c >= x1c and y2c >= y1c:
        clear_region(arr, x1c, y1c, x2c, y2c)

# 4) For each color-filtered strip: clear target colors but PRESERVE detected text block (if any)
for (sx1, sy1, sx2, sy2), text_range in strip_text_ranges.items():
    sx1c, sy1c, sx2c, sy2c = sx1, sy1, sx2, sy2
    if text_range is None:
        # No text -> clear target colors across whole strip
        clear_region_by_exact_colors(arr, sx1c, sy1c, sx2c, sy2c, TARGET_COLORS_RGBA, match_alpha=MATCH_ALPHA)
    else:
        tstart, tend = text_range
        # Clear above text block (if any)
        if tstart > sy1c:
            clear_region_by_exact_colors(arr, sx1c, sy1c, sx2c, tstart - 1, TARGET_COLORS_RGBA, match_alpha=MATCH_ALPHA)
        # Clear below text block (if any)
        if tend < sy2c:
            clear_region_by_exact_colors(arr, sx1c, tend + 1, sx2c, sy2c, TARGET_COLORS_RGBA, match_alpha=MATCH_ALPHA)
        # Leave the text block rows untouched (so text remains)

# 5) Save back (Pillow optimize)
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)

# 6) Optional: run optipng for better lossless compression
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
        print(f"ℹ️ optipng not found on PATH. Pillow only: {bytes_to_kb(before)} → {bytes_to_kb(os.path.getsize(IMAGE_PATH))}")
else:
    after = os.path.getsize(IMAGE_PATH)
    print(f"Done. Saved (Pillow only): {bytes_to_kb(before)} → {bytes_to_kb(after)}")
