import os
from PIL import Image
import numpy as np

# commit
# ==== CONFIG - set your folder path and thresholds here ====
FOLDER_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\Pages\MOD1\300\ORG\check"
IMAGE_EXTENSION = ".png"

# thresholds (set as fraction, e.g. 0.85 == 85%)
VERTICAL_THRESHOLD = 0.70       # Keep if above this ratio (black+transparent)
HORIZONTAL_THRESHOLD = 0.60     # Keep if above this ratio (black+transparent)
SAFEGUARD_THRESHOLD = 0.35      # Keep if above this ratio AND previous 3 were kept

# ==== UNCONDITIONAL AREAS ====
AREAS_TO_CLEAR = [
    (0,    0, 1151,    3),   # Top 3 rows
    (0, 2043, 1151, 2047),   # Bottom 5 rows
    (0,    0,    2, 2047),   # First 3 columns
    (1149, 0, 1151, 2047),   # Last 3 columns

    (0, 0, 535, 59),         # Top start left
    (611, 0, 1151, 59),      # Top start right

    (0, 1988, 526, 2047),    # Bottom end left
    (625, 1988, 1151, 2047), # Bottom end right
]

# ==== CONDITIONAL STRIPS / CHUNKS ====
VERTICAL_STRIPS = [
    (0, 4, 52, 2042),        # Left vertical strip
    (1099, 4, 1151, 2042),   # Right vertical strip
]

HORIZONTAL_CHUNKS = [
    (0,    4,  1151,  59),   # Top left chunk
    (0, 1988,  1151, 2042),  # Bottom chunk
]

# HORIZONTAL_CHUNKS = [
#     (0,    4,  538,  59),   # Top left chunk
#     (608,    4,  1151,  59),   # Top right chunk
#     (0, 1988,  531, 2042),  # Bottom chunk
#     (626, 1988,  1151, 2042),  # Bottom chunk
# ]

# ---------------- helpers ----------------
def clamp_rect(x1, y1, x2, y2, w, h):
    """Return inclusive clamped rectangle coordinates."""
    x1, x2 = sorted((int(x1), int(x2)))
    y1, y2 = sorted((int(y1), int(y2)))
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w - 1))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h - 1))
    return x1, y1, x2, y2

def pixel_type_ratios2(pixels):
    """Return (black_ratio, transparent_ratio, other_ratio) between 0 and 1."""
    a = pixels[..., 3]
    rgb = pixels[..., :3]
    is_transparent = (a == 0)
    is_black = np.all(rgb == 0, axis=-1)
    is_other = ~(is_transparent | is_black)

    total = pixels.shape[0]
    if total == 0:
        return 0.0, 0.0, 0.0
    return (is_black.sum() / total,
            is_transparent.sum() / total,
            is_other.sum() / total)


def pixel_type_ratios(pixels):
    """
    Returns black%, transparent%, and other% as floats between 0 and 1.
    Percentages are mutually exclusive and sum to 1.0.
    """
    a = pixels[..., 3]
    rgb = pixels[..., :3]

    tolerance = 10  # treat near-black as black
    is_transparent = (a == 0)
    is_black_opaque = (a > 0) & np.all(rgb <= tolerance, axis=-1)
    is_other = ~(is_transparent | is_black_opaque)

    total = pixels.shape[0]
    if total == 0:
        return 0.0, 0.0, 0.0

    return (
        is_black_opaque.sum() / total,  # black %
        is_transparent.sum() / total,   # transparent %
        is_other.sum() / total          # other %
    )



# ---------------- processing functions ----------------
def process_single_image(path):
    print(f"\nProcessing: {path}")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]

    # 1) Unconditional clears
    for (x1, y1, x2, y2) in AREAS_TO_CLEAR:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c >= x1c and y2c >= y1c:
            arr[y1c:y2c+1, x1c:x2c+1, 3] = 0
            arr[y1c:y2c+1, x1c:x2c+1, 0:3] = 0
            print(f"  [UNC] Cleared area ({x1c},{y1c})-({x2c},{y2c})")

    total_removed = 0

    # 2) Vertical strips: row-by-row
    for (x1, y1, x2, y2) in VERTICAL_STRIPS:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c < x1c or y2c < y1c:
            continue
        width = x2c - x1c + 1
        print(f"  [VERT STRIP] checking ({x1c},{y1c})-({x2c},{y2c}) rows {y1c}..{y2c}")

        # prev_keeps = [False, False, False]  # oldest first
        prev_keeps = [False, False]  # oldest first

        for y in range(y1c, y2c + 1):
            row = arr[y, x1c:x2c + 1]
            black_ratio, trans_ratio, other_ratio = pixel_type_ratios(row)
            ratio = black_ratio + trans_ratio

            keep = False
            if trans_ratio == 1.0 or black_ratio == 1.0:
                keep = False
            elif ratio > VERTICAL_THRESHOLD:
                keep = True
            elif ratio > SAFEGUARD_THRESHOLD and all(prev_keeps):
                keep = True
            else:
                keep = False

            print(f"    Row {y}: black={black_ratio:.2%}, transparent={trans_ratio:.2%}, other={other_ratio:.2%}", end="")
            if keep:
                print("  -> kept")
            else:
                arr[y, x1c:x2c + 1, 3] = 0
                arr[y, x1c:x2c + 1, 0:3] = 0
                total_removed += width
                print("  -> REMOVED")

            prev_keeps.pop(0)
            prev_keeps.append(keep)

    # 3) Horizontal chunks: column-by-column
    for (x1, y1, x2, y2) in HORIZONTAL_CHUNKS:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c < x1c or y2c < y1c:
            continue
        height = y2c - y1c + 1
        print(f"  [HORIZ CHUNK] checking ({x1c},{y1c})-({x2c},{y2c}) cols {x1c}..{x2c}")

        # prev_keeps = [False, False, False]  # oldest first
        prev_keeps = [False, False]  # oldest first

        for x in range(x1c, x2c + 1):
            col = arr[y1c:y2c + 1, x]
            black_ratio, trans_ratio, other_ratio = pixel_type_ratios(col)
            ratio = black_ratio + trans_ratio

            keep = False
            if trans_ratio == 1.0 or black_ratio == 1.0:
                keep = False
            elif ratio > HORIZONTAL_THRESHOLD:
                keep = True
            elif ratio > SAFEGUARD_THRESHOLD and all(prev_keeps):
                keep = True
            else:
                keep = False

            print(f"    Col {x}: black={black_ratio:.2%}, transparent={trans_ratio:.2%}, other={other_ratio:.2%}", end="")
            if keep:
                print("  -> kept")
            else:
                arr[y1c:y2c + 1, x, 3] = 0
                arr[y1c:y2c + 1, x, 0:3] = 0
                total_removed += height
                print("  -> REMOVED")

            prev_keeps.pop(0)
            prev_keeps.append(keep)

    # 4) Save in-place
    Image.fromarray(arr).save(path, format="PNG", optimize=True, compress_level=9)
    print(f"  ✅ Saved (removed approx. {total_removed} pixels).")

# ---------------- main ----------------
def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print("FOLDER_PATH must be an existing directory.")
        return
    files = sorted(os.listdir(folder_path))
    pngs = [f for f in files if f.lower().endswith(IMAGE_EXTENSION)]
    if not pngs:
        print("No PNG files found in folder.")
        return
    for fname in pngs:
        full = os.path.join(folder_path, fname)
        try:
            process_single_image(full)
        except Exception as e:
            print(f"Error processing {fname}: {e}")

if __name__ == "__main__":
    process_folder(FOLDER_PATH)
