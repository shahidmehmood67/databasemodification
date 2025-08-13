from PIL import Image
import numpy as np
import os
import shutil
import subprocess

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page003.png"
RUN_OPTIPNG = False          # set False if you don't want to run optipng
OPTIPNG_ARGS = ["-o7", "-quiet"]   # lossless compression; no chunk stripping (keeps metadata)

# All rectangles to clear: (x1, y1, x2, y2)
AREAS_TO_CLEAR = [

    # Static blocks
    (0, 0, 1151, 3),       # Top 3 rows
    (0, 2043, 1151, 2047), # Bottom last 5 rows
    (0, 0, 2, 2047),       # First 3 columns
    (1149, 0, 1151, 2047), # Last 3 columns

    # Left vertical strip
    (0, 60, 52, 1987),

    # Right vertical strip
    (1099, 60, 1151, 1987),

    # Top-left chunk strips
    *[(0, y, 552, y) for y in range(4, 60)],

    # Top-right chunk strips
    *[(603, y, 1151, y) for y in range(4, 60)],

    # Bottom-left chunk strips
    *[(0, y, 528, y) for y in range(1988, 2043)],

    # Bottom-right chunk strips
    *[(627, y, 1151, y) for y in range(1988, 2043)]
]



def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

def clamp_rect(x1, y1, x2, y2, w, h):
    # Ensure x1<=x2, y1<=y2 and clamp inside image bounds
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2

# 1) Load image as RGBA
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)  # shape: (h, w, 4)
h, w = arr.shape[:2]

# 2) Clear requested rectangles (alpha=0; RGB=0)
for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
    x1, y1, x2, y2 = clamp_rect(x1, y1, x2, y2, w, h)
    if x2 >= x1 and y2 >= y1:
        arr[y1:y2+1, x1:x2+1, 3] = 0      # alpha -> transparent
        arr[y1:y2+1, x1:x2+1, 0:3] = 0    # RGB -> black (invisible when alpha=0)

# 3) Save (lossless) with Pillow; let Pillow infer mode (avoids deprecation warning)
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)

# 4) Optional: run optipng (lossless recompression)
if RUN_OPTIPNG:
    optipng_path = shutil.which("optipng")
    if optipng_path:
        try:
            subprocess.run([optipng_path, *OPTIPNG_ARGS, IMAGE_PATH], check=True)
            after = os.path.getsize(IMAGE_PATH)
            print(f"✅ OptiPNG: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
        except subprocess.CalledProcessError as e:
            after = os.path.getsize(IMAGE_PATH)
            print(f"⚠️ OptiPNG error (kept Pillow output). Size: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
    else:
        after = os.path.getsize(IMAGE_PATH)
        print(f"ℹ️ optipng not found on PATH. Pillow only: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
else:
    after = os.path.getsize(IMAGE_PATH)
    print(f"ℹ️ Skipped OptiPNG. Size: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
