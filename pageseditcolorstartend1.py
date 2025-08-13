from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page006.png"

# Left and right strip columns (x1, x2)
LEFT_STRIP = (0, 52)       # inclusive x1, exclusive x2
RIGHT_STRIP = (1099, 1151) # inclusive x1, exclusive x2

# Colors to treat as "remove" candidates (black border style)
REMOVE_COLOR = (0, 0, 0)  # RGB pure black

BLANK_ROW_THRESHOLD = 2  # number of consecutive blank rows to trigger pause/resume

def is_blank_row(row_pixels):
    """Check if row is fully transparent or black"""
    # row_pixels shape: (width, 4) RGBA
    alpha = row_pixels[:, 3]
    rgb = row_pixels[:, :3]
    # blank if all alpha=0 OR all RGB = black with alpha > 0
    if np.all(alpha == 0):
        return True
    if np.all((rgb == REMOVE_COLOR).all(axis=1)):
        return True
    return False

def process_strip(arr, x1, x2):
    h = arr.shape[0]
    mode = "remove"  # start by removing
    blank_count = 0

    for y in range(h):
        row = arr[y, x1:x2, :]
        if is_blank_row(row):
            blank_count += 1
        else:
            blank_count = 0

        if mode == "remove":
            if blank_count >= BLANK_ROW_THRESHOLD:
                mode = "pause"
            else:
                # remove this row in the strip
                arr[y, x1:x2, 3] = 0
                arr[y, x1:x2, 0:3] = 0
        elif mode == "pause":
            if blank_count >= BLANK_ROW_THRESHOLD:
                # We saw another blank gap → resume removing
                mode = "remove"

    return arr

# ==== MAIN ====
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)

# Process left and right strips separately
arr = process_strip(arr, LEFT_STRIP[0], LEFT_STRIP[1])
arr = process_strip(arr, RIGHT_STRIP[0], RIGHT_STRIP[1])

# Save
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)

print("✅ Processing done for left/right strips.")
