from PIL import Image
import numpy as np
import os
import shutil
import subprocess

IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page003.png"

def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

# 1) Load & modify pixels (keep your logic here)
img = Image.open(IMAGE_PATH).convert("RGBA")
pixels = np.array(img)
h, w = pixels.shape[:2]

# Example: top 3 rows, bottom 5 rows, left 3 cols, right 3 cols → transparent
pixels[0:3, :, 3] = 0;  pixels[0:3, :, 0:3] = 0
pixels[h-5:h, :, 3] = 0; pixels[h-5:h, :, 0:3] = 0
pixels[:, 0:3, 3] = 0;  pixels[:, 0:3, 0:3] = 0
pixels[:, w-3:w, 3] = 0; pixels[:, w-3:w, 0:3] = 0

# 2) Save with Pillow using highest compression (still lossless)
img_out = Image.fromarray(pixels)  # let Pillow infer mode
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
img_out.save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)

# 3) Run optipng if available (lossless recompression)
# optipng = shutil.which("optipng")  # finds it on PATH
# if optipng is not None:
#     # -o7 = max effort (slowest, best compression)
#     # -strip safe = remove non-essential chunks safely (keeps color profile/gamma)
#     # subprocess.run([optipng, "-o7", "-strip", "safe", "-quiet", IMAGE_PATH], check=True)
#     # subprocess.run([optipng, "-o7", "-quiet", IMAGE_PATH], check=True)
#     subprocess.run([optipng, "-o7", "-strip", "all", "-quiet", IMAGE_PATH], check=True)
#
#     after = os.path.getsize(IMAGE_PATH)
#     print(f"✅ Optimized with optipng: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
# else:
#     after = os.path.getsize(IMAGE_PATH)
#     print(f"ℹ️ optipng not found on PATH. Saved with Pillow only: {bytes_to_kb(before)} → {bytes_to_kb(after)}")
