# from PIL import Image
# import numpy as np
# import os
#
# # ==== CONFIG ====
# IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
# TARGET_COLORS_RGBA = np.array([
#     [161, 156, 118, 255],  # #a19c76
#     [162, 156, 118, 255],  # #a29c76
#     [204, 204, 153, 255],  # #cccc99
#     [102, 51, 51, 255],  # #663333
#     [234, 234, 234, 255],  # #eaeaea
#     [0, 0, 0, 255],  # #000000 black
# ], dtype=np.uint8)
# LEFT_STRIP = (0, 60, 52, 1987)
# RIGHT_STRIP = (1099, 60, 1151, 1987)
# FUZZY_THRESHOLD = 0.05  # treat row as blank if <5% pixels have color
#
# # ------------------------------- helpers -----------------------------------
# def bytes_to_kb(b):
#     return f"{b/1024:.0f} KB"
#
# def clamp_rect(x1, y1, x2, y2, w, h):
#     x1, x2 = sorted((int(x1), int(x2)))
#     y1, y2 = sorted((int(y1), int(y2)))
#     x1 = max(0, min(x1, w - 1))
#     x2 = max(0, min(x2, w - 1))
#     y1 = max(0, min(y1, h - 1))
#     y2 = max(0, min(y2, h - 1))
#     return x1, y1, x2, y2
#
# def clear_colors_in_rows(arr, x1, x2, row_indices, target_colors):
#     removed_pixels = 0
#     for y in row_indices:
#         row = arr[y, x1:x2+1]  # (width,4)
#         cmp = (row[None, :, :] == target_colors[:, None, :])
#         matches_any = np.any(np.all(cmp, axis=-1), axis=0)
#         if matches_any.any():
#             idx = np.nonzero(matches_any)[0]
#             arr[y, x1+idx, 3] = 0
#             arr[y, x1+idx, 0:3] = 0
#             removed_pixels += int(matches_any.sum())
#     return removed_pixels
#
# def detect_protected_rows(arr, x1, x2, y1, y2, fuzzy_thresh=FUZZY_THRESHOLD):
#     """Detect text blocks protected between blank row sequences."""
#     protected = np.zeros(y2-y1+1, dtype=bool)
#     blank_count = 0
#     in_text_block = False
#     height = y2 - y1 + 1
#
#     for i, y in enumerate(range(y1, y2+1)):
#         row = arr[y, x1:x2+1]  # shape (width,4)
#         colored_pixels = np.count_nonzero(row[:, 3] > 0)  # count pixels with alpha>0
#         if colored_pixels / row.shape[0] < fuzzy_thresh:
#             # row is considered blank
#             blank_count += 1
#             if blank_count >= 2:
#                 in_text_block = False
#         else:
#             # row has text/color
#             if not in_text_block:
#                 in_text_block = True
#             protected[i] = True
#             blank_count = 0
#     # Convert to row indices relative to full image
#     return np.nonzero(protected)[0] + y1
#
# # ------------------------------- main --------------------------------------
# img = Image.open(IMAGE_PATH).convert("RGBA")
# arr = np.array(img)
# h, w = arr.shape[:2]
# before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
# print(f"Loaded {IMAGE_PATH} ({w}x{h}) size_before={bytes_to_kb(before)}")
#
# total_removed = 0
# for strip in [LEFT_STRIP, RIGHT_STRIP]:
#     x1, y1, x2, y2 = clamp_rect(*strip, w=w, h=h)
#     protected_rows = detect_protected_rows(arr, x1, x2, y1, y2)
#     all_rows = np.arange(y1, y2+1)
#     removable_rows = np.setdiff1d(all_rows, protected_rows)
#     removed = clear_colors_in_rows(arr, x1, x2, removable_rows, TARGET_COLORS_RGBA)
#     total_removed += removed
#     print(f"Strip {strip}: removed_pixels={removed}, protected_rows={len(protected_rows)}")
#
# # Save the modified image
# Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
# after = os.path.getsize(IMAGE_PATH)
# print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")

from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
TARGET_COLORS_RGBA = np.array([
    [161, 156, 118, 255],  # #a19c76
    [162, 156, 118, 255],  # #a29c76
    [204, 204, 153, 255],  # #cccc99
    [102,  51,  51, 255],  # #663333
    [234, 234, 234, 255],  # #eaeaea
    [0,    0,   0, 255],   # #000000 black
], dtype=np.uint8)

LEFT_STRIP  = (0, 60, 52, 1987)
RIGHT_STRIP = (1099, 60, 1151, 1987)
FUZZY_THRESHOLD = 0.05  # treat row as blank if <5% pixels have color

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

def clear_colors_in_rows(arr, x1, x2, row_indices, target_colors):
    removed_pixels = 0
    for y in row_indices:
        row = arr[y, x1:x2+1]  # (width,4)
        cmp = (row[None, :, :] == target_colors[:, None, :])
        matches_any = np.any(np.all(cmp, axis=-1), axis=0)
        if matches_any.any():
            idx = np.nonzero(matches_any)[0]
            arr[y, x1+idx, 3] = 0      # alpha -> transparent
            arr[y, x1+idx, 0:3] = 0    # RGB -> black (invisible)
            removed_pixels += int(matches_any.sum())
    return removed_pixels

def detect_protected_rows(arr, x1, x2, y1, y2, fuzzy_thresh=FUZZY_THRESHOLD):
    """Detect text blocks protected between blank row sequences."""
    protected = np.zeros(y2-y1+1, dtype=bool)
    blank_count = 0
    in_text_block = False

    for i, y in enumerate(range(y1, y2+1)):
        row = arr[y, x1:x2+1]
        colored_pixels = np.count_nonzero(row[:, 3] > 0)
        if colored_pixels / row.shape[0] < fuzzy_thresh:
            blank_count += 1
            if blank_count >= 2:
                in_text_block = False
        else:
            in_text_block = True
            protected[i] = True
            blank_count = 0

    return np.nonzero(protected)[0] + y1

# ------------------------------- main --------------------------------------
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)
h, w = arr.shape[:2]
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
print(f"Loaded {IMAGE_PATH} ({w}x{h}) size_before={bytes_to_kb(before)}")

total_removed = 0
for strip in [LEFT_STRIP, RIGHT_STRIP]:
    x1, y1, x2, y2 = clamp_rect(*strip, w=w, h=h)
    protected_rows = detect_protected_rows(arr, x1, x2, y1, y2)
    all_rows = np.arange(y1, y2+1)
    removable_rows = np.setdiff1d(all_rows, protected_rows)
    removed = clear_colors_in_rows(arr, x1, x2, removable_rows, TARGET_COLORS_RGBA)
    total_removed += removed
    print(f"Strip {strip}: removed_pixels={removed}, protected_rows={len(protected_rows)}")

# Save the modified image
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
after = os.path.getsize(IMAGE_PATH)
print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")
