import sqlite3
import json

DB_PATH = r"H:\Other Projects\Python\db\quran.sqlite"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def get_marker(hezb, quarter):
    cursor.execute("""
        SELECT soraid, ayaid
        FROM aya
        WHERE hezb = ?
          AND quarter = ?
          AND quarterstart = 1
        ORDER BY soraid, ayaid
        LIMIT 1
    """, (hezb, quarter))

    row = cursor.fetchone()

    if row:
        return {
            "surah": row["soraid"],
            "ayah": row["ayaid"]
        }

    return None


result = {}

for juz in range(1, 31):

    first_hezb = (juz - 1) * 2 + 1
    second_hezb = first_hezb + 1

    result[f"Juz {juz}"] = {
        "Start": get_marker(first_hezb, 1),
        "Quarter": get_marker(first_hezb, 3),
        "Half": get_marker(second_hezb, 1),
        "ThreeQuarter": get_marker(second_hezb, 3)
    }

with open("juz_markers.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print("JSON created successfully.")