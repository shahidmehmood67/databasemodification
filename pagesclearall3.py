from PIL import Image
import numpy as np
import os

# ==== CONFIG ====
FOLDER_PATH = r"D:\Assets\modified\pages\MODSHORT\2"
# FOLDER_PATH = r"D:\Assets\modified\pages\MOD"
IMAGE_EXTENSION = ".png"

# Unconditional areas to clear (always made transparent)
AREAS_TO_CLEAR = [
    (0, 0, 1151, 2),         # Top 3 rows (y=0..2)
    (0, 2043, 1151, 2047),   # Bottom last 5 rows (y=2043..2047)
    (0, 0, 2, 2047),         # First 3 columns (x=0..2)
    (1149, 0, 1151, 2047),   # Last 3 columns  (x=1149..1151)
]

# Vertical strips for conditional, row-wise removal (same logic as before)
VERTICAL_STRIPS = [
    (0, 60, 52, 1987),        # Left vertical strip
    (1099, 60, 1151, 1987),   # Right vertical strip
]

# Horizontal chunks treated as whole blocks (block-level ratio decision)
# Use inclusive coords; code below indexes [y1:y2+1, x1:x2+1]
HORIZONTAL_BLOCKS = [
    (0,    4,  552,  59),   # Top-left chunk   (y=4..59, x=0..552)
    (603,  4, 1151,  59),   # Top-right chunk  (y=4..59, x=603..1151)
    (0, 1988,  528, 2042),  # Bottom-left chunk (y=1988..2042, x=0..528)
    (627,1988, 1151, 2042), # Bottom-right chunk (y=1988..2042, x=627..1151)
]

# Behavior tuning
BLANK_ROW_THRESHOLD = 2              # consecutive "blank" rows to pause removal in vertical strips
BLACK_TRANSPARENT_THRESHOLD = 0.65   # >=85% black or transparent => treat as blank (skip removal)

# ------------------------------- helpers -----------------------------------
def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

def clamp_rect(x1, y1, x2, y2, w, h):
    # normalize and clamp (inclusive)
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

def black_or_transparent_mask(block):
    """Return boolean mask (h,w) for black (#000) OR fully transparent (A==0)."""
    rgb_black = np.all(block[..., :3] == 0, axis=-1)
    a = block[..., 3]
    is_trans = (a == 0)
    is_black_opaque = rgb_black & (a == 255)
    return is_trans | is_black_opaque

def clear_strip_conditional_rowwise(arr, x1, x2, y1, y2,
                                    black_trans_ratio_threshold,
                                    blank_row_threshold):
    """
    Vertical strips: decide per row.
    - If row is mostly black/transparent (ratio >= threshold) -> SKIP removal
    - If we encounter consecutive blank rows >= threshold        -> pause removal
    - Else remove whole row (set all pixels in the strip transparent)
    """
    consecutive_blank = 0
    total_removed = 0

    for y in range(y1, y2 + 1):
        row = arr[y, x1:x2+1]  # (width, 4)
        total_pixels = row.shape[0]

        # ratios
        mask_bt = black_or_transparent_mask(row[None, ...]).reshape(-1)  # (width,)
        ratio_black_trans = mask_bt.sum() / total_pixels

        colored_pixels = np.count_nonzero(np.any(row[:, :3] != 0, axis=1))
        ratio_colored = colored_pixels / total_pixels

        # "blank" row detection (<1% colored means blank)
        if ratio_colored < 0.01:
            consecutive_blank += 1
        else:
            consecutive_blank = 0

        # removal decision
        remove_row = True
        if ratio_black_trans >= black_trans_ratio_threshold:
            remove_row = False
        elif consecutive_blank >= blank_row_threshold:
            remove_row = False

        removed_this_row = 0
        if remove_row:
            arr[y, x1:x2+1, 3] = 0
            arr[y, x1:x2+1, 0:3] = 0
            removed_this_row = total_pixels
            total_removed += removed_this_row

        # Debug
        print(
            f"Row {y}: black_trans={ratio_black_trans:.2%}, colored={ratio_colored:.2%}, "
            f"remove={remove_row}, removed_px={removed_this_row}"
        )

    return total_removed

def clear_block_conditional(arr, x1, y1, x2, y2, black_trans_ratio_threshold, label="block"):
    """
    Horizontal chunks: treat the WHOLE rectangle as a single unit.
    - Compute black/transparent ratio for the entire block.
    - If block is mostly black/transparent (ratio >= threshold) -> SKIP removal
    - Else remove entire block (set all transparent).
    """
    block = arr[y1:y2+1, x1:x2+1]  # (h, w, 4)
    total_pixels = block.shape[0] * block.shape[1]
    if total_pixels == 0:
        print(f"{label}: empty after clamp; skipped")
        return 0

    mask_bt = black_or_transparent_mask(block)
    ratio_black_trans = mask_bt.sum() / total_pixels

    # Decision: same rule as strips (skip if mostly black/transparent)
    remove_block = ratio_black_trans < black_trans_ratio_threshold

    removed_px = 0
    if remove_block:
        block[..., 3] = 0
        block[..., :3] = 0
        removed_px = total_pixels

    # Write back
    arr[y1:y2+1, x1:x2+1] = block

    print(
        f"{label}: area=({x1},{y1})-({x2},{y2}) "
        f"black_trans={ratio_black_trans:.2%} -> remove={remove_block}, removed_px={removed_px}"
    )
    return removed_px

# ------------------------------- main --------------------------------------
# Walk folder recursively
for root, _, files in os.walk(FOLDER_PATH):
    for file in sorted(files):
        if not file.lower().endswith(IMAGE_EXTENSION):
            continue

        IMAGE_PATH = os.path.join(root, file)
        print(f"\nProcessing {IMAGE_PATH} ...")

        img = Image.open(IMAGE_PATH).convert("RGBA")
        arr = np.array(img)
        h, w = arr.shape[:2]
        before = os.path.getsize(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else 0

        # 1) Unconditional clears
        for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
            x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
            if x2c >= x1c and y2c >= y1c:
                clear_region(arr, x1c, y1c, x2c, y2c)

        # 2) Conditional vertical strips (row-wise)
        total_removed = 0
        for strip in VERTICAL_STRIPS:
            xs1, ys1, xs2, ys2 = clamp_rect(*strip, w=w, h=h)
            removed = clear_strip_conditional_rowwise(
                arr, xs1, xs2, ys1, ys2,
                BLACK_TRANSPARENT_THRESHOLD,
                BLANK_ROW_THRESHOLD
            )
            total_removed += removed
            print(f"Vertical strip {strip} -> removed_px={removed}")

        # 3) Conditional horizontal blocks (block-level)
        for i, block in enumerate(HORIZONTAL_BLOCKS, start=1):
            xb1, yb1, xb2, yb2 = clamp_rect(*block, w=w, h=h)
            removed = clear_block_conditional(
                arr, xb1, yb1, xb2, yb2,
                BLACK_TRANSPARENT_THRESHOLD,
                label=f"Horizontal block {i}"
            )
            total_removed += removed

        # 4) Save image (lossless)
        Image.fromarray(arr).save(IMAGE_PATH, format="PNG", optimize=True, compress_level=9)
        after = os.path.getsize(IMAGE_PATH)
        print(f"Saved: {bytes_to_kb(before)} -> {bytes_to_kb(after)}, total_removed={total_removed}")
