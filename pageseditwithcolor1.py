# from PIL import Image
# import numpy as np
# import os
#
# # ==== CONFIG ====
# IMAGE_PATH = r"D:\Assets\modified\pages\MOD\page005.png"
#
# # Target colors to remove
# TARGET_COLORS_RGBA = np.array([
#     [161, 156, 118, 255],  # #a19c76
#     [162, 156, 118, 255],  # #a29c76
#     [204, 204, 153, 255],  # #cccc99
#     [102,  51,  51, 255],  # #663333
#     [234, 234, 234, 255],  # #eaeaea
#     [0,    0,   0, 255],   # #000000 black
# ], dtype=np.uint8)
#
# # Strips
# LEFT_STRIP  = (0, 60, 52, 1987)
# RIGHT_STRIP = (1099, 60, 1151, 1987)
#
# # Behavior tuning
# BLANK_ROW_THRESHOLD = 2       # consecutive blank rows to pause removal
# BLANK_RATIO = 0.01            # row is considered blank if <1% pixels have color
# BLACK_TRANSPARENT_THRESHOLD = 0.85  # rows mostly black/transparent => skip
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
# def clear_strip_with_combined_logic(arr, x1, x2, y1, y2, target_colors, blank_threshold, blank_ratio, black_trans_ratio):
#     total_removed = 0
#     consecutive_blank = 0
#     removing_enabled = True
#
#     for y in range(y1, y2+1):
#         row = arr[y, x1:x2+1]
#         total_pixels = row.shape[0]
#
#         # Compute black+transparent ratio
#         black_or_trans = np.count_nonzero(
#             (np.all(row[:, :3] == 0, axis=1) & ((row[:, 3] == 255) | (row[:, 3] == 0)))
#         )
#         ratio_black_trans = black_or_trans / total_pixels
#
#         # Skip removing if mostly black+transparent
#         if ratio_black_trans >= black_trans_ratio:
#             removing_enabled = False
#         else:
#             # Determine blank row
#             colored_pixels = np.count_nonzero(np.any(row[:, :3] != 0, axis=1))
#             ratio_colored = colored_pixels / total_pixels
#             if ratio_colored < blank_ratio:
#                 consecutive_blank += 1
#             else:
#                 consecutive_blank = 0
#
#             # Pause removal if consecutive blank rows reached threshold
#             if consecutive_blank >= blank_threshold:
#                 removing_enabled = False
#             elif consecutive_blank == 0:
#                 removing_enabled = True
#
#         if removing_enabled:
#             # Remove only target colors in this row
#             cmp = (row[None, :, :] == target_colors[:, None, :])
#             matches_any = np.any(np.all(cmp, axis=-1), axis=0)
#             if matches_any.any():
#                 idx = np.nonzero(matches_any)[0]
#                 arr[y, x1+idx, 3] = 0
#                 arr[y, x1+idx, 0:3] = 0
#                 total_removed += int(matches_any.sum())
#
#     return total_removed
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
#     removed = clear_strip_with_combined_logic(
#         arr, x1, x2, y1, y2, TARGET_COLORS_RGBA,
#         BLANK_ROW_THRESHOLD, BLANK_RATIO, BLACK_TRANSPARENT_THRESHOLD
#     )
#     total_removed += removed
#     print(f"Strip {strip}: removed_pixels={removed}")
#
# # Save the modified image
# Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
# after = os.path.getsize(IMAGE_PATH)
# print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")

from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
IMAGE_PATH = r"D:\Assets\modified\pages\MOD\page030.png"

# Target colors to remove
TARGET_COLORS_RGBA = np.array([
    [161, 156, 118, 255],  # #a19c76
    [162, 156, 118, 255],  # #a29c76
    [204, 204, 153, 255],  # #cccc99
    [102,  51,  51, 255],  # #663333
    [234, 234, 234, 255],  # #eaeaea
    [0,    0,   0, 255],   # #000000 black
], dtype=np.uint8)

# Strips
LEFT_STRIP  = (0, 60, 52, 1987)
RIGHT_STRIP = (1099, 60, 1151, 1987)

# Behavior tuning
BLANK_ROW_THRESHOLD = 2       # consecutive blank rows to pause removal
BLANK_RATIO = 0.01            # row is considered blank if <1% pixels have color
BLACK_TRANSPARENT_THRESHOLD = 0.65  # rows mostly black/transparent => skip

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

def clear_strip_with_debug(arr, x1, x2, y1, y2, target_colors, blank_threshold, blank_ratio, black_trans_ratio):
    total_removed = 0
    consecutive_blank = 0
    removing_enabled = True

    for y in range(y1, y2+1):
        row = arr[y, x1:x2+1]
        total_pixels = row.shape[0]

        # Compute black+transparent ratio
        black_or_trans = np.count_nonzero(
            (np.all(row[:, :3] == 0, axis=1) & ((row[:, 3] == 255) | (row[:, 3] == 0)))
        )
        ratio_black_trans = black_or_trans / total_pixels

        # Determine if row is blank (few colored pixels)
        colored_pixels = np.count_nonzero(np.any(row[:, :3] != 0, axis=1))
        ratio_colored = colored_pixels / total_pixels
        if ratio_colored < blank_ratio:
            consecutive_blank += 1
        else:
            consecutive_blank = 0

        # Decide if removal is allowed
        if ratio_black_trans >= black_trans_ratio:
            removing_enabled = False
        elif consecutive_blank >= blank_threshold:
            removing_enabled = False
        else:
            removing_enabled = True

        # Remove only target colors if allowed
        removed_this_row = 0
        if removing_enabled:
            cmp = (row[None, :, :] == target_colors[:, None, :])
            matches_any = np.any(np.all(cmp, axis=-1), axis=0)
            if matches_any.any():
                idx = np.nonzero(matches_any)[0]
                arr[y, x1+idx, 3] = 0
                arr[y, x1+idx, 0:3] = 0
                removed_this_row = int(matches_any.sum())
                total_removed += removed_this_row

        # Debug print
        print(f"Row {y}: black_trans_ratio={ratio_black_trans:.2%}, colored_ratio={ratio_colored:.2%}, "
              f"removing_enabled={removing_enabled}, removed_pixels={removed_this_row}")

    return total_removed

# ------------------------------- main --------------------------------------
img = Image.open(IMAGE_PATH).convert("RGBA")
arr = np.array(img)
h, w = arr.shape[:2]
before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0
print(f"Loaded {IMAGE_PATH} ({w}x{h}) size_before={bytes_to_kb(before)}")

total_removed = 0
for strip in [LEFT_STRIP, RIGHT_STRIP]:
    x1, y1, x2, y2 = clamp_rect(*strip, w=w, h=h)
    removed = clear_strip_with_debug(
        arr, x1, x2, y1, y2, TARGET_COLORS_RGBA,
        BLANK_ROW_THRESHOLD, BLANK_RATIO, BLACK_TRANSPARENT_THRESHOLD
    )
    total_removed += removed
    print(f"Strip {strip}: removed_pixels={removed}")

# Save the modified image
Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
after = os.path.getsize(IMAGE_PATH)
print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")
