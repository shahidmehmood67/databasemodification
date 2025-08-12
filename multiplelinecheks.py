import sqlite3
from collections import defaultdict

# ==== CONFIG ====
db2_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\ORG\ayahinfo_1152.db"

# ==== CONNECT ====
conn = sqlite3.connect(db2_path)
cur = conn.cursor()

# ==== GET DATA ====
cur.execute("""
    SELECT sura_number, ayah_number, line_number
    FROM glyphs
    GROUP BY sura_number, ayah_number, line_number
""")
rows = cur.fetchall()

# ==== GROUP BY sura/ayah and count unique lines ====
line_counts = defaultdict(set)
for sura, aya, line in rows:
    line_counts[(sura, aya)].add(line)

# ==== FIND MULTI-LINE AYAT ====
multi_line_ayat = {k: v for k, v in line_counts.items() if len(v) > 1}

# ==== PRINT ====
print(f"Total ayahs with multiple lines: {len(multi_line_ayat)}\n")
for (sura, aya), lines in sorted(multi_line_ayat.items()):
    print(f"Sura {sura}, Ayah {aya} -> Lines: {sorted(lines)}")

# ==== CLOSE ====
conn.close()
