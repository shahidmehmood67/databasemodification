# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


import sqlite3
import json
import os
from collections import defaultdict

# ===== CONFIGURATION =====
DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"  # Change to your SQLite file path
OUTPUT_DIR = "output_pages"            # Folder where JSON files will be saved
TABLE_NAME = "ayarects"                   # Change if your table name is different
# =========================

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Read all rows ordered logically
cursor.execute(f"""
    SELECT soraid, ayaid, page, line, word, minx, maxx, miny, maxy
    FROM {TABLE_NAME}
    ORDER BY page, soraid, ayaid, line, word
""")

rows = cursor.fetchall()
conn.close()

# Data structure: page → surahs → ayahs → list of line objects
pages_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for soraid, ayaid, page, line, word, minx, maxx, miny, maxy in rows:
    surah = pages_data[page][soraid][ayaid]

    # Check if last entry in this ayah has same line & coordinates → merge word range
    if surah and surah[-1]["line"] == line \
       and surah[-1]["minx"] == minx and surah[-1]["maxx"] == maxx \
       and surah[-1]["miny"] == miny and surah[-1]["maxy"] == maxy:
        # Extend the word range
        if surah[-1]["words"]["end"] is None or word > surah[-1]["words"]["end"]:
            surah[-1]["words"]["end"] = word
    else:
        # Add a new line entry
        surah.append({
            "line": line,
            "words": {"start": word, "end": word},
            "minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy
        })

# Now pad each page to exactly 16 lines (placeholders at end)
for page, surahs in pages_data.items():
    # Count total lines across all surahs in the page
    total_lines = sum(len(lines) for ayahs in surahs.values() for lines in ayahs.values())

    while total_lines < 16:
        # Add placeholder to the last ayah of the last surah in the page
        last_sura_id = sorted(surahs.keys())[-1]
        last_ayah_id = sorted(surahs[last_sura_id].keys())[-1]
        surahs[last_sura_id][last_ayah_id].append({
            "line": None,
            "words": {"start": None, "end": None},
            "minx": None, "maxx": None, "miny": None, "maxy": None
        })
        total_lines += 1

# Save each page to a separate JSON file
for page, surahs in pages_data.items():
    output = {
        "page": page,
        "surahs": surahs,
        "total_lines": 16
    }
    with open(os.path.join(OUTPUT_DIR, f"page_{page:03}.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Export completed. Files saved in '{OUTPUT_DIR}' folder.")

