import os
from PIL import Image
import numpy as np

# ==== CONFIG - set your folder path here ====
FOLDER_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\Pages\MOD1\600\cut"
IMAGE_EXTENSION = ".png"

# ==== PER-PAGE CLEARING CONFIG ====
# Key = Quran page number (logical), Value = list of rectangles (x1, y1, x2, y2)
AREAS_TO_CLEAR = {
    528: [  # Page 600, but filename will be 599.png
        (0, 0, 1151, 3),  # Top 3 rows
        (0, 2042, 1151, 2047),  # Bottom 5 rows
        (0, 0, 2, 2047),  # First 3 columns
        (1144, 0, 1151, 2047),  # Last 3 columns

        (0, 0, 52, 2047),        # left side
        (1099, 0, 1151, 838),        # right side
        (1099, 963, 1151, 1453),        # right side
        (1099, 1580, 1151, 2047),        # right side


        (0, 0, 538, 59),  # Top start left
        (605, 0, 1151, 59),  # Top start right

        (0, 1988, 523, 2047),  # Bottom end left
        (624, 1988, 1151, 2047)  # Bottom end right
    ],
    # Add more pages as needed...
}


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


# ---------------- processing functions ----------------
def process_single_image(path, page_number, rects):
    print(f"\n📄 Processing page={page_number} (file: {os.path.basename(path)})")
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]

    # Apply unconditional clears
    for (x1, y1, x2, y2) in rects:
        x1c, y1c, x2c, y2c = clamp_rect(x1, y1, x2, y2, w, h)
        if x2c >= x1c and y2c >= y1c:
            arr[y1c:y2c+1, x1c:x2c+1, 3] = 0
            arr[y1c:y2c+1, x1c:x2c+1, 0:3] = 0
            print(f"   ✅ Cleared area ({x1c},{y1c})-({x2c},{y2c})")

    # Save back in-place
    Image.fromarray(arr).save(path, format="PNG", optimize=True, compress_level=9)
    print(f"   💾 Saved {os.path.basename(path)}")


def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print("❌ FOLDER_PATH must be an existing directory.")
        return

    files = sorted(os.listdir(folder_path))
    pngs = [f for f in files if f.lower().endswith(IMAGE_EXTENSION)]
    if not pngs:
        print("⚠️ No PNG files found in folder.")
        return

    # Build reverse mapping: filename number -> config page
    filename_to_page = {page - 1: page for page in AREAS_TO_CLEAR.keys()}

    for fname in pngs:
        try:
            basename = os.path.splitext(fname)[0]   # e.g. "page599"
            if not basename.startswith("page"):
                print(f"⚠️ Skipping unexpected filename: {fname}")
                continue
            page_from_filename = int(basename.replace("page", ""))  # "page599" → 599
        except ValueError:
            print(f"⚠️ Skipping invalid filename: {fname}")
            continue

        if page_from_filename not in filename_to_page:
            # Skip files without config
            print(f"↩️ Skipping {fname} (no config for page {page_from_filename + 1})")
            continue

        page_number = filename_to_page[page_from_filename]
        rects = AREAS_TO_CLEAR[page_number]
        full_path = os.path.join(folder_path, fname)

        try:
            process_single_image(full_path, page_number, rects)
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")


if __name__ == "__main__":
    process_folder(FOLDER_PATH)

