from PIL import Image
import numpy as np
import os
import shutil
import subprocess

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
RUN_OPTIPNG = False                 # True to run optipng after save (must be on PATH)
OPTIPNG_ARGS = ["-o7", "-quiet"]    # lossless recompression
MATCH_ALPHA = True                  # require alpha to match target RGBA when removing

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
BLANK_ROW_THRESHOLD = 4   # consecutive blank rows required to toggle pause/remove
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

# ---------------------------- strip processor -------------------------------
def process_strip_with_blank_toggle(arr, sx1, sy1, sx2, sy2, target_colors_rgba, match_alpha=True,
                                    blank_threshold=BLANK_ROW_THRESHOLD):
    """
    Scan rows top->bottom inside the inclusive box [sx1..sx2, sy1..sy2].
    Toggle between 'remove' and 'pause' whenever there are `blank_threshold` consecutive blank rows.
    In 'remove' mode, remove pixels that exactly match target_colors_rgba.
    Returns statistics (removed_pixel_count, toggle_events).
    """
    h, w = arr.shape[:2]
    sx1c, sy1c, sx2c, sy2c = clamp_rect(sx1, sy1, sx2, sy2, w, h)

    targets = target_colors_rgba
    if not match_alpha:
        targets = targets[:, :3]  # only RGB comparison

    mode = 'remove'  # start by removing (toggle logic will handle blank rows)
    blank_count = 0
    toggled_on_current_blank_run = False
    removed_pixels = 0
    toggle_events = []

    width = sx2c - sx1c + 1
    # Precompute shape helpers
    for y in range(sy1c, sy2c + 1):
        row = arr[y, sx1c:sx2c+1]  # shape (width,4)
        alpha = row[:, 3]
        # Consider a row blank only if all pixels are fully transparent (alpha == 0)
        is_blank = np.all(alpha == 0)

        if is_blank:
            blank_count += 1
        else:
            # blank run ended
            blank_count = 0
            toggled_on_current_blank_run = False

        # Toggle when we hit the threshold for the first time in this blank run
        if blank_count >= blank_threshold and not toggled_on_current_blank_run:
            old_mode = mode
            mode = 'pause' if mode == 'remove' else 'remove'
            toggled_on_current_blank_run = True
            toggle_events.append((y, old_mode, mode))
            # (debug print suppressed here; caller can inspect toggle_events)

        if mode == 'remove':
            # Create mask of pixels matching any target color in this row
            if match_alpha:
                # region shape (width,4). targets (n,4)
                # Compare: produce (n, width, 4) then all over channel -> (n,width), then any -> (width,)
                cmp = (row[None, :, :] == targets[:, None, :])  # (n, width, 4)
                matches_any = np.any(np.all(cmp, axis=-1), axis=0)
            else:
                # compare only RGB
                cmp = (row[None, :, :3] == targets[:, None, :3])
                matches_any = np.any(np.all(cmp, axis=-1), axis=0)

            if matches_any.any():
                # set those pixels transparent
                indices = np.nonzero(matches_any)[0]
                arr[y, sx1c + indices, 3] = 0
                arr[y, sx1c + indices, 0:3] = 0
                removed_pixels += int(matches_any.sum())

    return removed_pixels, toggle_events

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

# 2) Process left/right strips with blank-row toggling, removing only target colors
total_removed = 0
all_toggle_events = {}
for (sx1, sy1, sx2, sy2) in COLOR_FILTERED_STRIPS:
    removed, toggles = process_strip_with_blank_toggle(
        arr, sx1, sy1, sx2, sy2, TARGET_COLORS_RGBA, match_alpha=MATCH_ALPHA
    )
    total_removed += removed
    all_toggle_events[(sx1, sy1, sx2, sy2)] = toggles
    print(f"Strip {(sx1,sy1,sx2,sy2)}: removed pixels={removed}, toggles={len(toggles)}")

# Print toggle event summaries (row where toggle occurred and mode change)
for strip, events in all_toggle_events.items():
    if events:
        print(f"  Toggle events for {strip}:")
        for ev in events:
            print(f"    at row {ev[0]}: {ev[1]} -> {ev[2]}")

# 3) Save (Pillow)
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
after = os.path.getsize(IMAGE_PATH)
print(f"Saved (Pillow): {bytes_to_kb(before)} -> {bytes_to_kb(after)}  total_removed={total_removed}")

# 4) Optional: optipng
if RUN_OPTIPNG:
    optipng_path = shutil.which("optipng")
    if optipng_path:
        try:
            subprocess.run([optipng_path, *OPTIPNG_ARGS, IMAGE_PATH], check=True)
            after2 = os.path.getsize(IMAGE_PATH)
            print(f"OptiPNG: {bytes_to_kb(after)} -> {bytes_to_kb(after2)}")
        except subprocess.CalledProcessError:
            print("OptiPNG failed; kept Pillow-only file.")
    else:
        print("optipng not found on PATH; skipped external optimization.")
