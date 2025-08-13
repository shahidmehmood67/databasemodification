from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page003.png"  # Change to your PNG file
BLOCK_WIDTH = 100   # Width of block (in pixels)
BLOCK_HEIGHT = 100  # Height of block (in pixels)

# ==== LOAD IMAGE ====
if not os.path.exists(IMAGE_PATH):
    print(f"❌ File not found: {IMAGE_PATH}")
    exit()

img = Image.open(IMAGE_PATH).convert("RGBA")  # Keep alpha if exists
width, height = img.size

# Convert to NumPy array for pixel access
pixels = np.array(img)

# ==== BASIC INFO ====
total_pixels = width * height
megapixels = total_pixels / 1_000_000

print("📄 IMAGE INFO")
print(f"Path         : {IMAGE_PATH}")
print(f"Format       : {img.format or 'Unknown'}")
print(f"Mode         : {img.mode}")
print(f"Width        : {width} px")
print(f"Height       : {height} px")
print(f"Total Pixels : {total_pixels:,} ({megapixels:.2f} MP)")

# ==== ROWS & COLUMNS ====
print("\n📏 ROWS & COLUMNS")
print(f"Rows (Y-axis): {height}")
print(f"Cols (X-axis): {width}")

# ==== BLOCK INFO ====
rows_in_blocks = height // BLOCK_HEIGHT
cols_in_blocks = width // BLOCK_WIDTH
print("\n🗂 BLOCK INFO")
print(f"Block Size     : {BLOCK_WIDTH}x{BLOCK_HEIGHT} px")
print(f"Blocks Row-wise: {rows_in_blocks}")
print(f"Blocks Col-wise: {cols_in_blocks}")
print(f"Total Blocks   : {rows_in_blocks * cols_in_blocks}")

# ==== SAMPLE PIXEL ====
sample_x, sample_y = 0, 0
sample_pixel = pixels[sample_y, sample_x]  # (Y, X) in NumPy
print("\n🎯 SAMPLE PIXEL")
print(f"Pixel at (0,0): {tuple(sample_pixel)}  # (R,G,B,A)")

# ==== SAMPLE BLOCK ====
print("\n🔍 SAMPLE BLOCK (Top-Left)")
block = pixels[0:BLOCK_HEIGHT, 0:BLOCK_WIDTH]  # Slice top-left block
print(f"Block shape: {block.shape}  # (height, width, channels)")
