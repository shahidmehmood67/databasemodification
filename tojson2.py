#!/usr/bin/env python3
"""
SQLite -> per-page JSON exporter for your ayarects table.

- Groups words by page -> soraid -> ayaid -> line
- Merges word rows on same line into one line-object with words.start / words.end
- Keeps all original rows for that line under "raw_data"
- Ensures each page has exactly 16 lines (pads with null placeholders appended to last surah/ayah)
- Writes one JSON file per page to avoid large single-file editing

Adjust DB_PATH, OUTPUT_DIR, TABLE_NAME at top if needed.
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict
import sys

# ----------------- CONFIG (already set to what you posted) -----------------
DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"
OUTPUT_DIR = Path(r"D:\Assets\modified\v1\output_json")
TABLE_NAME = "ayarects"
# -------------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REQ_COLS = {"soraid", "ayaid", "page", "line", "word", "minx", "maxx", "miny", "maxy"}

def fetch_and_export():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # quick schema check so user-friendly errors show up
    cur.execute(f"PRAGMA table_info({TABLE_NAME})")
    cols_info = cur.fetchall()
    if not cols_info:
        print(f"ERROR: table '{TABLE_NAME}' not found in DB '{DB_PATH}'.")
        print("Available tables (simple list):")
        tcur = conn.cursor()
        for r in tcur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            print(" -", r[0])
        conn.close()
        sys.exit(1)

    actual_cols = {c["name"] for c in cols_info}
    if not REQ_COLS.issubset(actual_cols):
        print("ERROR: required columns not all present in the table.")
        print("Required:", sorted(REQ_COLS))
        print("Found   :", sorted(actual_cols))
        print("If column names differ, edit the SELECT below to match your schema.")
        conn.close()
        sys.exit(1)

    # main query (matches your earlier / requested ordering)
    query = f"""
        SELECT soraid, ayaid, page, line, word, minx, maxx, miny, maxy
        FROM {TABLE_NAME}
        ORDER BY page, soraid, ayaid, line, word
    """

    cur.execute(query)

    # Nested structure:
    # pages_data[page][soraid][ayaid][line] -> list of row dicts (each word row)
    pages_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    print("Reading rows and grouping (this may take a few seconds)...")
    row_count = 0
    for row in cur:
        # row is sqlite3.Row (mapping)
        soraid = int(row["soraid"])
        ayaid = int(row["ayaid"])
        page = int(row["page"])
        # line may be int or null; ensure int if possible
        line_val = row["line"]
        line = int(line_val) if line_val is not None else None
        word = row["word"]

        # build a minimal raw row dict, keeping exactly the fields we selected
        raw = {
            "soraid": soraid,
            "ayaid": ayaid,
            "page": page,
            "line": line,
            "word": word,
            "minx": row["minx"],
            "maxx": row["maxx"],
            "miny": row["miny"],
            "maxy": row["maxy"],
        }
        pages_data[page][soraid][ayaid][line].append(raw)
        row_count += 1
        if row_count % 20000 == 0:
            print(f"  processed {row_count} rows...")

    conn.close()
    print(f"Total rows processed: {row_count}")
    print("Building per-page JSON and saving files...")

    saved_pages = 0
    # iterate pages in sorted order
    for page in sorted(pages_data.keys()):
        surahs = pages_data[page]
        page_obj = {"page": page, "surahs": {}, "total_lines": 16}

        # build structure per surah/ayah
        for soraid in sorted(surahs.keys()):
            surah_obj = {"ayahs": {}}
            ayahs = surahs[soraid]
            for ayaid in sorted(ayahs.keys()):
                lines_dict = ayahs[ayaid]  # dict: line_num -> list(raw rows)
                ayah_lines = []
                # lines in sorted order (line may be None but normal pages should have numeric lines)
                for line_num in sorted(lines_dict.keys(), key=lambda x: (x is None, x)):
                    line_rows = lines_dict[line_num]
                    # compute merged values, ignoring None values when calculating min/max
                    words_nonnull = [r["word"] for r in line_rows if r["word"] is not None]
                    if words_nonnull:
                        word_start = min(words_nonnull)
                        word_end = max(words_nonnull)
                    else:
                        word_start = None
                        word_end = None

                    # for bounding boxes use numerical mins/maxs if present else None
                    minx_vals = [r["minx"] for r in line_rows if r["minx"] is not None]
                    maxx_vals = [r["maxx"] for r in line_rows if r["maxx"] is not None]
                    miny_vals = [r["miny"] for r in line_rows if r["miny"] is not None]
                    maxy_vals = [r["maxy"] for r in line_rows if r["maxy"] is not None]

                    minx = min(minx_vals) if minx_vals else None
                    maxx = max(maxx_vals) if maxx_vals else None
                    miny = min(miny_vals) if miny_vals else None
                    maxy = max(maxy_vals) if maxy_vals else None

                    line_entry = {
                        "line": line_num,
                        "words": {"start": word_start, "end": word_end},
                        "minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy,
                        "raw_data": line_rows
                    }
                    ayah_lines.append(line_entry)

                # put ayah lines array (may be empty theoretically)
                surah_obj["ayahs"][str(ayaid)] = ayah_lines

            page_obj["surahs"][str(soraid)] = surah_obj

        # count total line-objects across all ayahs on the page
        def count_lines(page_obj):
            cnt = 0
            for s in page_obj["surahs"].values():
                for a in s["ayahs"].values():
                    cnt += len(a)
            return cnt

        total_lines = count_lines(page_obj)

        # pad placeholders at the end (append to last surah -> last ayah)
        if total_lines < 16:
            # pick last surah and ayah (sorted by numeric value)
            last_sora_keys = sorted(int(k) for k in page_obj["surahs"].keys())
            if not last_sora_keys:
                # theoretically empty page; create a dummy surah/ayah
                page_obj["surahs"]["1"] = {"ayahs": {"1": []}}
                last_sura_id = 1
                last_ayah_id = 1
            else:
                last_sura_id = last_sora_keys[-1]
                last_ayah_keys = sorted(int(k) for k in page_obj["surahs"][str(last_sura_id)]["ayahs"].keys())
                if not last_ayah_keys:
                    # create a default ayah under last surah
                    page_obj["surahs"][str(last_sura_id)]["ayahs"]["1"] = []
                    last_ayah_id = 1
                else:
                    last_ayah_id = last_ayah_keys[-1]

            # append placeholders until total_lines == 16
            while total_lines < 16:
                placeholder = {
                    "line": None,
                    "words": {"start": None, "end": None},
                    "minx": None, "maxx": None, "miny": None, "maxy": None,
                    "raw_data": []
                }
                page_obj["surahs"][str(last_sura_id)]["ayahs"][str(last_ayah_id)].append(placeholder)
                total_lines += 1

        # save the page JSON file
        out_file = OUTPUT_DIR / f"page_{int(page):03d}.json"
        with out_file.open("w", encoding="utf-8") as fh:
            json.dump(page_obj, fh, ensure_ascii=False, indent=2)

        saved_pages += 1
        if saved_pages % 50 == 0:
            print(f"  saved {saved_pages} pages...")

    print(f"\n✅ Export finished. Saved {saved_pages} page files into: {OUTPUT_DIR}")

if __name__ == "__main__":
    fetch_and_export()
