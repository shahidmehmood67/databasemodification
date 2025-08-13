from PIL import Image
import numpy as np

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page003.png"

# ==== LOAD IMAGE ====
img = Image.open(IMAGE_PATH).convert("RGBA")  # Ensure alpha channel
pixels = np.array(img)

# ==== GET DIMENSIONS ====
height, width = pixels.shape[0], pixels.shape[1]

# ==== MAKE ROWS TRANSPARENT ====
# Top 3 rows
pixels[0:3, :, 3] = 0  # alpha channel = 0
pixels[0:3, :, 0:3] = 0  # RGB to black (optional, for clean transparency)

# Bottom 4 rows
pixels[height-5:height, :, 3] = 0
pixels[height-5:height, :, 0:3] = 0

# ==== MAKE COLUMNS TRANSPARENT ====
# Left 3 columns
pixels[:, 0:3, 3] = 0
pixels[:, 0:3, 0:3] = 0

# Right 3 columns
pixels[:, width-3:width, 3] = 0
pixels[:, width-3:width, 0:3] = 0

# ==== SAVE IMAGE (overwrite) ====
img_out = Image.fromarray(pixels, "RGBA")
# img_out.save(IMAGE_PATH, format="PNG")
img_out.save(IMAGE_PATH, format="PNG", optimize=True)


print("✅ Pixels made transparent successfully.")
