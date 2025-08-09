import sqlite3
import json
from pathlib import Path
from collections import defaultdict

DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"
OUTPUT_DIR = Path(r"D:\Assets\modified\v1\pagesv2inside")

def convert_sqlite_to_json():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(f"SELECT MAX(page) as max_page FROM ayarects")
    max_page = cur.fetchone()["max_page"]
    print(f"Max page found in DB: {max_page}")

    for page_num in range(1, max_page + 1):
        print(f"Processing page {page_num}...")

        cur.execute(f"""
            SELECT soraid, ayaid, page, line, word
            FROM ayarects
            WHERE page = ?
            ORDER BY line, soraid, ayaid, word
        """, (page_num,))

        rows = cur.fetchall()

        lines = defaultdict(lambda: defaultdict(list))

        for r in rows:
            line_num = r["line"]
            if line_num is None:
                continue
            key = (r["soraid"], r["ayaid"])
            lines[line_num][key].append(r["word"])

        page_json = {
            "page": page_num,
            "lines": []
        }

        for line_no in range(1, 17):
            ayahs_list = []
            if line_no in lines:
                for (soraid, ayaid), words in lines[line_no].items():
                    word_start = min(words)
                    word_end = max(words)
                    ayahs_list.append({
                        "soraid": soraid,
                        "ayaid": ayaid,
                        "words": {"start": word_start, "end": word_end}
                    })
            page_json["lines"].append({
                "line": line_no,
                "ayahs": ayahs_list
            })

        filename = OUTPUT_DIR / f"page_{page_num:03d}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(page_json, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"✅ Conversion complete. JSON files saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    convert_sqlite_to_json()
