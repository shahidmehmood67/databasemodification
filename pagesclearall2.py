from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
FOLDER_PATH = r"D:\Assets\modified\pages\MODSHORT\1"
IMAGE_EXTENSION = ".png"

# Unconditional areas to clear
AREAS_TO_CLEAR = [
    (0, 0, 1151, 2),         # Top 3 rows
    (0, 2043, 1151, 2047),   # Bottom last 5 rows
    (0, 0, 2, 2047),         # First 3 columns
    (1149, 0, 1151, 2047),   # Last 3 columns
]

# Vertical strips for conditional removal
COLOR_FILTERED_STRIPS = [
    (0, 60, 52, 1987),        # Left vertical strip
    (1099, 60, 1151, 1987),   # Right vertical strip

    # Top-left horizontal strip (4px to 60px)
    *[(0, y, 552, y) for y in range(4, 60)],
    # Top-right horizontal strip
    *[(603, y, 1151, y) for y in range(4, 60)],

    # Bottom-left horizontal strip (1988px to 2043px)
    *[(0, y, 528, y) for y in range(1988, 2043)],
    # Bottom-right horizontal strip
    *[(627, y, 1151, y) for y in range(1988, 2043)],
]

# Behavior tuning
BLANK_ROW_THRESHOLD = 2              # consecutive blank rows required to toggle removal
BLACK_TRANSPARENT_THRESHOLD = 0.65   # 85% black/transparent pixels => skip removal

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
    arr[y1:y2+1, x1:x2+1, 3] = 0
    arr[y1:y2+1, x1:x2+1, 0:3] = 0

def clear_strip_conditional(arr, x1, x2, y1, y2, black_trans_ratio, blank_threshold):
    consecutive_blank = 0
    total_removed = 0
    for y in range(y1, y2+1):
        row = arr[y, x1:x2+1]
        total_pixels = row.shape[0]

        black_or_trans = np.count_nonzero(
            (np.all(row[:, :3] == 0, axis=1) & ((row[:, 3] == 0) | (row[:, 3] == 255)))
        )
        ratio_black_trans = black_or_trans / total_pixels

        colored_pixels = np.count_nonzero(np.any(row[:, :3] != 0, axis=1))
        ratio_colored = colored_pixels / total_pixels

        if ratio_colored < 0.01:
            consecutive_blank += 1
        else:
            consecutive_blank = 0

        remove_row = True
        if ratio_black_trans >= black_trans_ratio:
            remove_row = False
        elif consecutive_blank >= blank_threshold:
            remove_row = False

        removed_this_row = 0
        if remove_row:
            arr[y, x1:x2+1, 3] = 0
            arr[y, x1:x2+1, 0:3] = 0
            removed_this_row = total_pixels
            total_removed += removed_this_row

        print(f"Row {y}: black_trans_ratio={ratio_black_trans:.2%}, colored_ratio={ratio_colored:.2%}, "
              f"remove={remove_row}, removed_pixels={removed_this_row}")
    return total_removed

# ------------------------------- main --------------------------------------
# Scan folder recursively
for root, _, files in os.walk(FOLDER_PATH):
    for file in sorted(files):
        if file.lower().endswith(IMAGE_EXTENSION):
            IMAGE_PATH = os.path.join(root, file)
            print(f"\nProcessing {IMAGE_PATH} ...")
            img = Image.open(IMAGE_PATH).convert("RGBA")
            arr = np.array(img)
            h, w = arr.shape[:2]
            before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0

            # Unconditional clears
            for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
                x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
                if x2c >= x1c and y2c >= y1c:
                    clear_region(arr, x1c, y1c, x2c, y2c)

            # Conditional strips
            total_removed = 0
            for strip in COLOR_FILTERED_STRIPS:
                x1, y1, x2, y2 = clamp_rect(*strip, w=w, h=h)
                removed = clear_strip_conditional(arr, x1, x2, y1, y2,
                                                  BLACK_TRANSPARENT_THRESHOLD,
                                                  BLANK_ROW_THRESHOLD)
                total_removed += removed
                print(f"Strip {strip}: total_removed_pixels={removed}")

            # Save image
            Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
            after = os.path.getsize(IMAGE_PATH)
            print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")
