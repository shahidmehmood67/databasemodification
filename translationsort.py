import os
import sqlite3

OLD_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji.db"

NEW_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_sorted.db"

if os.path.exists(NEW_DB):
    os.remove(NEW_DB)

src = sqlite3.connect(OLD_DB)
src_cur = src.cursor()

dst = sqlite3.connect(NEW_DB)
dst_cur = dst.cursor()

dst_cur.execute("""
CREATE TABLE verses (
    sura INTEGER NOT NULL,
    ayah INTEGER NOT NULL,
    text TEXT,
    PRIMARY KEY (sura, ayah)
)
""")

src_cur.execute("""
SELECT sura, ayah, text
FROM verses
ORDER BY sura ASC, ayah ASC
""")

count = 0

while True:
    rows = src_cur.fetchmany(1000)

    if not rows:
        break

    dst_cur.executemany("""
        INSERT INTO verses (sura, ayah, text)
        VALUES (?, ?, ?)
    """, rows)

    count += len(rows)
    print(f"Copied {count}")

dst.commit()

src.close()
dst.close()

print(f"\nDone. Total verses copied: {count}")
print(f"New DB: {NEW_DB}")