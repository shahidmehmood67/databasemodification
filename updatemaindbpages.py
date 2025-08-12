# # # # # import sqlite3
# # # # #
# # # # # # ===== Hardcoded DB paths =====
# # # # # DB1_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\ayahinfo_1152.db"   # contains glyphs table
# # # # # DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"   # contains aya table
# # # # #
# # # # # # ===== Step 1: Connect to DB2 and duplicate table =====
# # # # # conn2 = sqlite3.connect(DB2_PATH)
# # # # # c2 = conn2.cursor()
# # # # #
# # # # # # Drop aya_indopak if exists (optional safety)
# # # # # c2.execute("DROP TABLE IF EXISTS aya_indopak")
# # # # #
# # # # # # Duplicate structure + data
# # # # # c2.execute("CREATE TABLE aya_indopak AS SELECT * FROM aya")
# # # # # conn2.commit()
# # # # #
# # # # # # ===== Step 2: Connect to DB1 =====
# # # # # conn1 = sqlite3.connect(DB1_PATH)
# # # # # c1 = conn1.cursor()
# # # # #
# # # # # # ===== Step 3: Update aya_indopak.page from glyphs =====
# # # # # # Get all mapping from glyphs: (sura_number, ayah_number) -> page_number
# # # # # c1.execute("""
# # # # #     SELECT sura_number, ayah_number, page_number
# # # # #     FROM glyphs
# # # # #     GROUP BY sura_number, ayah_number
# # # # # """)
# # # # # glyph_page_map = {(row[0], row[1]): row[2] for row in c1.fetchall()}
# # # # #
# # # # # # Update aya_indopak where ayaid > 0
# # # # # for (soraid, ayaid, _) in c2.execute("SELECT soraid, ayaid, page FROM aya_indopak WHERE ayaid > 0"):
# # # # #     if (soraid, ayaid) in glyph_page_map:
# # # # #         new_page = glyph_page_map[(soraid, ayaid)]
# # # # #         c2.execute("UPDATE aya_indopak SET page = ? WHERE soraid = ? AND ayaid = ?", (new_page, soraid, ayaid))
# # # # #
# # # # # # ===== Step 4: Handle ayaid = 0 case =====
# # # # # # For each sura, set ayaid=0 page same as ayaid=1
# # # # # c2.execute("SELECT DISTINCT soraid FROM aya_indopak WHERE ayaid = 0")
# # # # # for (soraid,) in c2.fetchall():
# # # # #     c2.execute("SELECT page FROM aya_indopak WHERE soraid = ? AND ayaid = 1", (soraid,))
# # # # #     res = c2.fetchone()
# # # # #     if res:
# # # # #         page_for_sura = res[0]
# # # # #         c2.execute("UPDATE aya_indopak SET page = ? WHERE soraid = ? AND ayaid = 0", (page_for_sura, soraid))
# # # # #
# # # # # conn2.commit()
# # # # #
# # # # # # ===== Close connections =====
# # # # # conn1.close()
# # # # # conn2.close()
# # # # #
# # # # # print("✅ aya_indopak updated successfully.")
# # # #
# # # # import sqlite3
# # # # import os
# # # #
# # # # # ===== Path to DB2 =====
# # # # DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# # # #
# # # # # Check file exists
# # # # if not os.path.exists(DB2_PATH):
# # # #     raise FileNotFoundError(f"Database not found: {DB2_PATH}")
# # # #
# # # # # Connect to DB2
# # # # conn = sqlite3.connect(DB2_PATH)
# # # # c = conn.cursor()
# # # #
# # # # # Step 1: Add column page_indopak if it doesn't exist
# # # # c.execute("PRAGMA table_info(aya)")
# # # # columns = [row[1] for row in c.fetchall()]
# # # # if "page_indopak" not in columns:
# # # #     c.execute("ALTER TABLE aya ADD COLUMN page_indopak INTEGER")
# # # #     print("✅ Added column page_indopak to aya.")
# # # #
# # # # # Step 2: Copy data from aya_indopak.page → aya.page_indopak
# # # # c.execute("""
# # # #     UPDATE aya
# # # #     SET page_indopak = (
# # # #         SELECT page FROM aya_indopak
# # # #         WHERE aya_indopak.soraid = aya.soraid
# # # #         AND aya_indopak.ayaid = aya.ayaid
# # # #     )
# # # # """)
# # # # print("✅ Copied page values from aya_indopak to aya.page_indopak.")
# # # #
# # # # # Step 3: Delete aya_indopak table
# # # # c.execute("DROP TABLE IF EXISTS aya_indopak")
# # # # print("✅ Deleted table aya_indopak.")
# # # #
# # # # # Commit and close
# # # # conn.commit()
# # # # conn.close()
# # # #
# # # # print("🎉 All done.")
# # # #
# # #
# # #
# # # import sqlite3
# # # import os
# # #
# # # # ===== Paths =====
# # # DB1_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# # # DB2_UPDATED_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quranupdated.sqlite"
# # #
# # # # ===== Check files =====
# # # if not os.path.exists(DB1_PATH):
# # #     raise FileNotFoundError(f"Database not found: {DB1_PATH}")
# # # if not os.path.exists(DB2_UPDATED_PATH):
# # #     raise FileNotFoundError(f"Database not found: {DB2_UPDATED_PATH}")
# # #
# # # # ===== Connect to DB1 (destination) =====
# # # conn1 = sqlite3.connect(DB1_PATH)
# # # c1 = conn1.cursor()
# # #
# # # # Add page_indopak column if missing
# # # c1.execute("PRAGMA table_info(aya)")
# # # columns_db1 = [row[1] for row in c1.fetchall()]
# # # if "page_indopak" not in columns_db1:
# # #     c1.execute("ALTER TABLE aya ADD COLUMN page_indopak INTEGER")
# # #     print("✅ Added column page_indopak to DB1 aya table.")
# # #
# # # # ===== Connect to DB2 (source) =====
# # # conn2 = sqlite3.connect(DB2_UPDATED_PATH)
# # # c2 = conn2.cursor()
# # #
# # # # Get mapping of (soraid, ayaid) → page_indopak from DB2
# # # c2.execute("SELECT soraid, ayaid, page_indopak FROM aya WHERE page_indopak IS NOT NULL")
# # # page_map = c2.fetchall()
# # #
# # # # ===== Update DB1 with page_indopak from DB2 =====
# # # for soraid, ayaid, page_indopak in page_map:
# # #     c1.execute("""
# # #         UPDATE aya
# # #         SET page_indopak = ?
# # #         WHERE soraid = ? AND ayaid = ?
# # #     """, (page_indopak, soraid, ayaid))
# # #
# # # conn1.commit()
# # #
# # # # ===== Close connections =====
# # # conn1.close()
# # # conn2.close()
# # #
# # # print("🎉 page_indopak copied from DB2 to DB1 successfully.")
# #
# # import sqlite3
# # import os
# #
# # # ===== Paths =====
# # DB1_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\ayahinfo_1152.db"  # glyphs
# # DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"      # aya
# #
# # # ===== Check files =====
# # if not os.path.exists(DB1_PATH):
# #     raise FileNotFoundError(f"Database not found: {DB1_PATH}")
# # if not os.path.exists(DB2_PATH):
# #     raise FileNotFoundError(f"Database not found: {DB2_PATH}")
# #
# # # ===== Connect to DB1 (glyphs) =====
# # conn1 = sqlite3.connect(DB1_PATH)
# # c1 = conn1.cursor()
# #
# # # Get page_number for each (sura_number, ayah_number)
# # c1.execute("""
# #     SELECT sura_number, ayah_number, page_number
# #     FROM glyphs
# #     GROUP BY sura_number, ayah_number
# # """)
# # glyph_map = {(s, a): p for s, a, p in c1.fetchall()}
# #
# # # ===== Connect to DB2 (aya) =====
# # conn2 = sqlite3.connect(DB2_PATH)
# # c2 = conn2.cursor()
# #
# # # Make sure page_indopak exists
# # c2.execute("PRAGMA table_info(aya)")
# # columns = [row[1] for row in c2.fetchall()]
# # if "page_indopak" not in columns:
# #     c2.execute("ALTER TABLE aya ADD COLUMN page_indopak INTEGER")
# #     print("✅ Added column page_indopak to aya.")
# #
# # # ===== Update ayaid > 0 from glyphs =====
# # for soraid, ayaid in c2.execute("SELECT soraid, ayaid FROM aya WHERE ayaid > 0"):
# #     if (soraid, ayaid) in glyph_map:
# #         c2.execute("""
# #             UPDATE aya
# #             SET page_indopak = ?
# #             WHERE soraid = ? AND ayaid = ?
# #         """, (glyph_map[(soraid, ayaid)], soraid, ayaid))
# #
# # # ===== Handle ayaid = 0 =====
# # c2.execute("SELECT DISTINCT soraid FROM aya WHERE ayaid = 0")
# # for (soraid,) in c2.fetchall():
# #     c2.execute("SELECT page_indopak FROM aya WHERE soraid = ? AND ayaid = 1", (soraid,))
# #     res = c2.fetchone()
# #     if res and res[0] is not None:
# #         c2.execute("""
# #             UPDATE aya
# #             SET page_indopak = ?
# #             WHERE soraid = ? AND ayaid = 0
# #         """, (res[0], soraid))
# #
# # # Commit changes
# # conn2.commit()
# # conn1.close()
# # conn2.close()
# #
# # print("🎉 page_indopak updated from glyphs successfully.")
# #
# import sqlite3
# import os
#
# # ===== Paths =====
# DB1_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\ayahinfo_1152.db"  # glyphs
# DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"      # aya
#
# # ===== Check files =====
# if not os.path.exists(DB1_PATH):
#     raise FileNotFoundError(f"Database not found: {DB1_PATH}")
# if not os.path.exists(DB2_PATH):
#     raise FileNotFoundError(f"Database not found: {DB2_PATH}")
#
# # ===== Connect to DB1 (glyphs) =====
# conn1 = sqlite3.connect(DB1_PATH)
# c1 = conn1.cursor()
#
# # Show sample data from glyphs
# print("\n--- First 20 rows from glyphs ---")
# for row in c1.execute("SELECT sura_number, ayah_number, page_number FROM glyphs LIMIT 20"):
#     print(row)
#
# # Get mapping of (sura_number, ayah_number) -> page_number
# c1.execute("""
#     SELECT sura_number, ayah_number, page_number
#     FROM glyphs
#     GROUP BY sura_number, ayah_number
# """)
# glyph_map = {(int(s), int(a)): int(p) for s, a, p in c1.fetchall()}
#
# print(f"\nTotal entries in glyph_map: {len(glyph_map)}")
#
# # ===== Connect to DB2 (aya) =====
# conn2 = sqlite3.connect(DB2_PATH)
# c2 = conn2.cursor()
#
# # Show sample data from aya
# print("\n--- First 20 rows from aya ---")
# for row in c2.execute("SELECT soraid, ayaid, page_indopak FROM aya LIMIT 20"):
#     print(row)
#
# # Make sure page_indopak exists
# c2.execute("PRAGMA table_info(aya)")
# columns = [row[1] for row in c2.fetchall()]
# if "page_indopak" not in columns:
#     c2.execute("ALTER TABLE aya ADD COLUMN page_indopak INTEGER")
#     print("✅ Added column page_indopak to aya.")
#
# # Debug: Check first 20 matches
# matches_found = 0
# print("\n--- First 20 matches between aya and glyphs ---")
# for soraid, ayaid in c2.execute("SELECT soraid, ayaid FROM aya WHERE ayaid > 0"):
#     key = (int(soraid), int(ayaid))
#     if key in glyph_map:
#         print(f"MATCH: soraid={soraid}, ayaid={ayaid} → page={glyph_map[key]}")
#         matches_found += 1
#         if matches_found >= 20:
#             break
#
# if matches_found == 0:
#     print("\n⚠ No matches found between aya and glyphs! Check if IDs align.")
# else:
#     # Run update
#     for soraid, ayaid in c2.execute("SELECT soraid, ayaid FROM aya WHERE ayaid > 0"):
#         key = (int(soraid), int(ayaid))
#         if key in glyph_map:
#             c2.execute("""
#                 UPDATE aya
#                 SET page_indopak = ?
#                 WHERE soraid = ? AND ayaid = ?
#             """, (glyph_map[key], soraid, ayaid))
#
#     # Handle ayaid = 0 case
#     c2.execute("SELECT DISTINCT soraid FROM aya WHERE ayaid = 0")
#     for (soraid,) in c2.fetchall():
#         c2.execute("SELECT page_indopak FROM aya WHERE soraid = ? AND ayaid = 1", (soraid,))
#         res = c2.fetchone()
#         if res and res[0] is not None:
#             c2.execute("""
#                 UPDATE aya
#                 SET page_indopak = ?
#                 WHERE soraid = ? AND ayaid = 0
#             """, (res[0], soraid))
#
#     conn2.commit()
#     print("\n🎉 page_indopak updated successfully.")
#
# # Close connections
# conn1.close()
# conn2.close()

import sqlite3

# ===== Paths to your DB files =====
DB1_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\ayahinfo_1152.db"  # glyphs table
DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"       # aya table

# ===== Connect to DBs =====
conn1 = sqlite3.connect(DB1_PATH)
conn2 = sqlite3.connect(DB2_PATH)
cur1 = conn1.cursor()
cur2 = conn2.cursor()

print("🔍 Step 1: Reading distinct sura_number, ayah_number, page_number from glyphs...")
cur1.execute("""
    SELECT sura_number, ayah_number, MIN(page_number) as page_number
    FROM glyphs
    GROUP BY sura_number, ayah_number
    ORDER BY sura_number, ayah_number
""")
glyphs_data = cur1.fetchall()
print(f"📄 Found {len(glyphs_data)} unique (sura, aya) entries in glyphs.")

matches_found = 0

print("\n🔍 Step 2: Updating aya.page_indopak in DB2...")
for sura, aya, page in glyphs_data:
    # Get current value for logging
    cur2.execute("""
        SELECT page_indopak FROM aya
        WHERE soraid = ? AND ayaid = ?
    """, (sura, aya))
    row = cur2.fetchone()

    if row is not None:
        old_value = row[0]
        cur2.execute("""
            UPDATE aya
            SET page_indopak = ?
            WHERE soraid = ? AND ayaid = ?
        """, (page, sura, aya))
        matches_found += 1
        print(f"✅ Updated Sura {sura}, Aya {aya}: {old_value} ➡ {page}")
    else:
        print(f"⚠ No match found in aya for Sura {sura}, Aya {aya}")

conn2.commit()

print("\n📊 Step 3: Update Summary")
print(f"🔹 Total rows matched & updated: {matches_found}")
print(f"🔹 Total DB changes recorded: {conn2.total_changes}")

conn1.close()
conn2.close()
print("🏁 Done. Please reopen your DB viewer to see the updated data.")
