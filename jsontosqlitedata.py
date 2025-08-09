import sqlite3
import json
from pathlib import Path

DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"
JSON_PATH = r"D:\Assets\modified\v1\pagesv2inside\page_004.json"

def update_page_from_json():
    # Load JSON
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    page_num = data['page']
    print(f"Updating DB for page {page_num} from JSON {JSON_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    allowed_pages = {page_num - 1, page_num, page_num + 1}

    for line in data['lines']:
        line_no = line['line']
        for ayah in line['ayahs']:
            soraid = ayah['soraid']
            ayaid = ayah['ayaid']
            word_start = ayah['words']['start']
            word_end = ayah['words']['end']

            cur.execute(f"""
                SELECT rowid, page, line FROM ayarects
                WHERE soraid = ? AND ayaid = ? AND word BETWEEN ? AND ?
                AND page IN ({','.join('?' for _ in allowed_pages)})
            """, (soraid, ayaid, word_start, word_end, *allowed_pages))

            rows_to_update = cur.fetchall()

            for row in rows_to_update:
                rowid, current_page, current_line = row
                if current_page != page_num or current_line != line_no:
                    cur.execute("""
                        UPDATE ayarects
                        SET page = ?, line = ?
                        WHERE rowid = ?
                    """, (page_num, line_no, rowid))
                    print(f"Updated rowid {rowid}: page {current_page} -> {page_num}, line {current_line} -> {line_no}")

    conn.commit()
    conn.close()
    print("✅ Update complete.")

if __name__ == "__main__":
    update_page_from_json()
