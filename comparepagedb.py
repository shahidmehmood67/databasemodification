# import sqlite3
# from collections import defaultdict
#
# # ==== CONFIG ====
# db1_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quranpages.sqlite"  # First DB (604 pages)
# db2_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\ORG\ayahinfo_1152.db"   # Second DB (611 pages)
# page_offset = 1  # DB2 page = DB1 page + 1
#
# # ==== CONNECT ====
# conn1 = sqlite3.connect(db1_path)
# conn2 = sqlite3.connect(db2_path)
# cur1 = conn1.cursor()
# cur2 = conn2.cursor()
#
# # ==== GET DISTINCT surah/ayah/page from DB1 ====
# cur1.execute("""
#     SELECT page, soraid, ayaid
#     FROM ayarects
#     GROUP BY page, soraid, ayaid
# """)
# db1_records = cur1.fetchall()
#
# # ==== GET DISTINCT surah/ayah/page from DB2 ====
# cur2.execute("""
#     SELECT page_number, sura_number, ayah_number
#     FROM glyphs
#     GROUP BY page_number, sura_number, ayah_number
# """)
# db2_records = cur2.fetchall()
#
# # Convert DB2 to a lookup set
# db2_set = set(db2_records)
#
# # ==== FIND MISSING IN DB2 ====
# missing_by_page = defaultdict(list)
# for page, sura, aya in db1_records:
#     db2_page = page + page_offset  # adjust page mapping
#     if (db2_page, sura, aya) not in db2_set:
#         missing_by_page[page].append((sura, aya))
#
# # ==== PRINT RESULTS ====
# for page in sorted(missing_by_page):
#     surah_ayah_list = ", ".join([f"S{s}:A{a}" for s, a in missing_by_page[page]])
#     print(f"Page {page}: Missing in DB2 -> {surah_ayah_list}")
#
# # ==== CLOSE ====
# conn1.close()
# conn2.close()

import sqlite3
from collections import defaultdict

# ==== CONFIG ====
db1_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quranpages.sqlite"  # First DB (604 pages)
db2_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\ORG\ayahinfo_1152.db"   # Second DB (611 pages)
page_offset = 1  # DB2 page = DB1 page + 1

# ==== CONNECT ====
conn1 = sqlite3.connect(db1_path)
conn2 = sqlite3.connect(db2_path)
cur1 = conn1.cursor()
cur2 = conn2.cursor()

# ==== GET DISTINCT surah/ayah/page from DB1 ====
cur1.execute("""
    SELECT page, soraid, ayaid
    FROM ayarects
    GROUP BY page, soraid, ayaid
""")
db1_records = cur1.fetchall()

# ==== GET DISTINCT surah/ayah/page from DB2 ====
cur2.execute("""
    SELECT page_number, sura_number, ayah_number
    FROM glyphs
    GROUP BY page_number, sura_number, ayah_number
""")
db2_records = cur2.fetchall()

# Convert DB2 to a lookup set
db2_set = set(db2_records)

# ==== FIND MISSING IN DB2 ====
missing_by_page = defaultdict(list)
for page, sura, aya in db1_records:
    db2_page = page + page_offset  # adjust page mapping
    if (db2_page, sura, aya) not in db2_set:
        missing_by_page[page].append((sura, aya))

# ==== PRINT RESULTS ====
for page in sorted(missing_by_page):
    surah_ayah_list = ", ".join([f"S{s}:A{a}" for s, a in missing_by_page[page]])
    print(f"Page {page}: Missing in DB2 -> {surah_ayah_list}")

# ==== CLOSE ====
conn1.close()
conn2.close()
