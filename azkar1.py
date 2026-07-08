import sqlite3
import json

DB_PATH = r"H:\Other Projects\Python\db\hisnul.sqlite3"
OUTPUT_JSON = r"H:\Other Projects\Python\db\dua_groups.json"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT _id, en_title FROM dua_group ORDER BY _id")

data = {
    str(_id): en_title or ""
    for _id, en_title in cursor.fetchall()
}

conn.close()

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Exported {len(data)} groups.")