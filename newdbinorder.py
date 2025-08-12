# # # # import sqlite3
# # # # import shutil
# # # # import os
# # # #
# # # # # ===== Paths =====
# # # # DB2_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# # # # DB2_NEW_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran_4th.sqlite"
# # # #
# # # # # Backup first
# # # # if os.path.exists(DB2_NEW_PATH):
# # # #     os.remove(DB2_NEW_PATH)
# # # # shutil.copy(DB2_PATH, DB2_NEW_PATH)
# # # #
# # # # # Open new DB
# # # # conn = sqlite3.connect(DB2_NEW_PATH)
# # # # cur = conn.cursor()
# # # #
# # # # # Get aya table columns
# # # # cur.execute("PRAGMA table_info(aya)")
# # # # columns = cur.fetchall()
# # # # col_names = [c[1] for c in columns]
# # # #
# # # # if "page_indopak" not in col_names:
# # # #     raise Exception("❌ Column 'page_indopak' not found in aya table.")
# # # #
# # # # # Build new column order
# # # # col_names.remove("page_indopak")
# # # # # Insert page_indopak at 4th position (index 3)
# # # # col_names.insert(3, "page_indopak")
# # # #
# # # # print("📋 New column order:", col_names)
# # # #
# # # # # Create CREATE TABLE statement with new order
# # # # cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='aya'")
# # # # create_sql = cur.fetchone()[0]
# # # #
# # # # # Extract column definitions from original CREATE statement
# # # # inside = create_sql[create_sql.find("(")+1:create_sql.rfind(")")]
# # # # columns_def = [c.strip() for c in inside.split(",")]
# # # #
# # # # # Map name -> definition
# # # # col_def_map = {}
# # # # for cdef in columns_def:
# # # #     name = cdef.split()[0].strip("`")
# # # #     col_def_map[name] = cdef
# # # #
# # # # # Build new CREATE TABLE for aya_new
# # # # new_col_defs = [col_def_map[name] for name in col_names]
# # # # new_create_sql = f"CREATE TABLE aya_new (\n  {',\n  '.join(new_col_defs)}\n)"
# # # # print("🛠 Creating new table with reordered columns...")
# # # # cur.execute(new_create_sql)
# # # #
# # # # # Copy data in new order
# # # # cols_str = ", ".join(col_names)
# # # # cur.execute(f"INSERT INTO aya_new ({cols_str}) SELECT {cols_str} FROM aya")
# # # #
# # # # # Drop old table and rename
# # # # cur.execute("DROP TABLE aya")
# # # # cur.execute("ALTER TABLE aya_new RENAME TO aya")
# # # #
# # # # conn.commit()
# # # # conn.close()
# # # #
# # # # print(f"✅ New DB created at {DB2_NEW_PATH} with 'page_indopak' as 4th column.")
# # #
# # # import sqlite3
# # # import shutil
# # # import os
# # #
# # # # ===== Paths =====
# # # DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# # # OUTPUT_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran_reorder.sqlite"
# # #
# # # # ===== Step 1: Backup original DB to output path =====
# # # shutil.copy(DB_PATH, OUTPUT_DB_PATH)
# # # print(f"Copied database to: {OUTPUT_DB_PATH}")
# # #
# # # # ===== Step 2: Connect to copied DB =====
# # # conn = sqlite3.connect(OUTPUT_DB_PATH)
# # # cur = conn.cursor()
# # #
# # # # ===== Step 3: Get the current column names for aya table =====
# # # cur.execute("PRAGMA table_info(aya)")
# # # columns_info = cur.fetchall()
# # # col_names = [col[1] for col in columns_info]
# # # print("Original columns in aya:", col_names)
# # #
# # # if "page_indopak" not in col_names:
# # #     raise ValueError("Column 'page_indopak' does not exist in aya table!")
# # #
# # # # ===== Step 4: Create a new aya table with reordered columns =====
# # # # Move page_indopak to 4th position
# # # new_order = col_names.copy()
# # # new_order.remove("page_indopak")
# # # new_order.insert(3, "page_indopak")
# # # print("New column order:", new_order)
# # #
# # # # Get CREATE TABLE statement of aya
# # # cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='aya'")
# # # create_sql = cur.fetchone()[0]
# # # print("Original CREATE SQL:", create_sql)
# # #
# # # # Modify CREATE TABLE to reorder columns
# # # # WARNING: This assumes the CREATE TABLE has columns in the same order as col_names
# # # col_defs = create_sql[create_sql.find("(")+1:create_sql.rfind(")")].split(",")
# # # col_defs = [c.strip() for c in col_defs]
# # #
# # # # Map col_name -> definition
# # # col_def_map = {}
# # # for definition in col_defs:
# # #     name = definition.split()[0].strip('"')
# # #     col_def_map[name] = definition
# # #
# # # # Rebuild ordered column definitions
# # # new_col_defs = [col_def_map[name] for name in new_order]
# # #
# # # # Create new aya table
# # # create_new_sql = f"CREATE TABLE aya_new ({', '.join(new_col_defs)})"
# # # print("CREATE TABLE aya_new SQL:", create_new_sql)
# # # cur.execute(create_new_sql)
# # #
# # # # ===== Step 5: Copy data into aya_new in new order =====
# # # cols_str = ", ".join(new_order)
# # # cur.execute(f"INSERT INTO aya_new ({cols_str}) SELECT {cols_str} FROM aya")
# # # print("Data copied to aya_new in new order.")
# # #
# # # # ===== Step 6: Drop old aya table and rename new =====
# # # cur.execute("DROP TABLE aya")
# # # cur.execute("ALTER TABLE aya_new RENAME TO aya")
# # # print("Replaced old aya table with reordered version.")
# # #
# # # # ===== Step 7: Compact the DB to remove free space =====
# # # conn.commit()
# # # print("Running VACUUM to shrink DB size...")
# # # cur.execute("VACUUM")
# # # conn.close()
# # #
# # # print(f"Done! New DB saved at: {OUTPUT_DB_PATH}")
# #
# # import sqlite3
# # import shutil
# # import os
# # import re
# #
# # # ===== Paths =====
# # DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# # OUTPUT_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran_reorde.sqlite"
# #
# # # ===== Step 1: Backup original DB to output path =====
# # shutil.copy(DB_PATH, OUTPUT_DB_PATH)
# # print(f"Copied database to: {OUTPUT_DB_PATH}")
# #
# # # ===== Step 2: Connect to copied DB =====
# # conn = sqlite3.connect(OUTPUT_DB_PATH)
# # cur = conn.cursor()
# #
# # # ===== Step 3: Get current columns =====
# # cur.execute("PRAGMA table_info(aya)")
# # columns_info = cur.fetchall()
# # col_names = [col[1] for col in columns_info]
# # print("Original columns in aya:", col_names)
# #
# # if "page_indopak" not in col_names:
# #     raise ValueError("Column 'page_indopak' does not exist in aya table!")
# #
# # # ===== Step 4: Prepare new column order =====
# # new_order = col_names.copy()
# # new_order.remove("page_indopak")
# # new_order.insert(3, "page_indopak")  # Move to 4th column
# # print("New column order:", new_order)
# #
# # # ===== Step 5: Extract CREATE TABLE aya =====
# # cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='aya'")
# # create_sql = cur.fetchone()[0]
# # print("Original CREATE TABLE SQL:", create_sql)
# #
# # # ===== Step 6: Parse column definitions safely =====
# # inside = create_sql[create_sql.find("(")+1:create_sql.rfind(")")]
# # col_defs = [c.strip() for c in inside.split(",")]
# #
# # # Normalize key names (remove quotes, lowercase)
# # def normalize(name):
# #     return name.strip('"').strip("'").lower()
# #
# # col_def_map = {}
# # for definition in col_defs:
# #     match = re.match(r'["\']?(\w+)["\']?\s+.*', definition)
# #     if match:
# #         name = normalize(match.group(1))
# #         col_def_map[name] = definition
# #
# # # ===== Step 7: Rebuild ordered column definitions =====
# # new_col_defs = [col_def_map[normalize(name)] for name in new_order]
# #
# # # ===== Step 8: Create new aya table =====
# # create_new_sql = f"CREATE TABLE aya_new ({', '.join(new_col_defs)})"
# # print("CREATE TABLE aya_new SQL:", create_new_sql)
# # cur.execute(create_new_sql)
# #
# # # ===== Step 9: Copy data in new order =====
# # cols_str = ", ".join(new_order)
# # cur.execute(f"INSERT INTO aya_new ({cols_str}) SELECT {cols_str} FROM aya")
# # print("Data copied to aya_new in new order.")
# #
# # # ===== Step 10: Replace old aya table =====
# # cur.execute("DROP TABLE aya")
# # cur.execute("ALTER TABLE aya_new RENAME TO aya")
# # print("Replaced old aya table with reordered version.")
# #
# # # ===== Step 11: Vacuum to reduce size =====
# # conn.commit()
# # print("Running VACUUM to shrink DB size...")
# # cur.execute("VACUUM")
# # conn.close()
# #
# # print(f"✅ Done! New DB saved at: {OUTPUT_DB_PATH}")
#
# import sqlite3
# import shutil
# import os
# import re
#
# # ===== Paths =====
# DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
# OUTPUT_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran_reorder.sqlite"
#
# # ===== Step 1: Backup original DB =====
# shutil.copy(DB_PATH, OUTPUT_DB_PATH)
# print(f"Copied database to: {OUTPUT_DB_PATH}")
#
# conn = sqlite3.connect(OUTPUT_DB_PATH)
# cur = conn.cursor()
#
# # ===== Step 2: Get current columns =====
# cur.execute("PRAGMA table_info(aya)")
# columns_info = cur.fetchall()
# col_names = [col[1] for col in columns_info]
# print("\n[DEBUG] Columns from PRAGMA:", col_names)
#
# if "page_indopak" not in col_names:
#     raise ValueError("Column 'page_indopak' does not exist in aya table!")
#
# # ===== Step 3: Prepare new column order =====
# new_order = col_names.copy()
# new_order.remove("page_indopak")
# new_order.insert(3, "page_indopak")
# print("[DEBUG] New column order:", new_order)
#
# # ===== Step 4: Get CREATE TABLE SQL =====
# cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='aya'")
# create_sql = cur.fetchone()[0]
# print("\n[DEBUG] Original CREATE TABLE SQL:\n", create_sql)
#
# # ===== Step 5: Extract column definitions =====
# inside = create_sql[create_sql.find("(")+1:create_sql.rfind(")")]
# col_defs = [c.strip() for c in inside.split(",")]
#
# def normalize(name):
#     return name.strip('"').strip("'").lower()
#
# col_def_map = {}
# for definition in col_defs:
#     match = re.match(r'["\']?(\w+)["\']?\s+.*', definition)
#     if match:
#         name_norm = normalize(match.group(1))
#         col_def_map[name_norm] = definition
#
# print("\n[DEBUG] Columns from CREATE TABLE:", list(col_def_map.keys()))
#
# # ===== Step 6: Check for mismatches =====
# for name in new_order:
#     if normalize(name) not in col_def_map:
#         print(f"[WARNING] Column '{name}' from PRAGMA not found in CREATE TABLE!")
#
# # ===== Step 7: Build new column definitions =====
# try:
#     new_col_defs = [col_def_map[normalize(name)] for name in new_order]
# except KeyError as e:
#     raise RuntimeError(f"Column {e} not found in CREATE TABLE. Check spelling!") from e
#
# # ===== Step 8: Create new table =====
# create_new_sql = f"CREATE TABLE aya_new ({', '.join(new_col_defs)})"
# print("\n[DEBUG] New CREATE TABLE aya_new SQL:\n", create_new_sql)
# cur.execute(create_new_sql)
#
# # ===== Step 9: Copy data =====
# cols_str = ", ".join(new_order)
# cur.execute(f"INSERT INTO aya_new ({cols_str}) SELECT {cols_str} FROM aya")
# print("[INFO] Data copied into new table in new order.")
#
# # ===== Step 10: Replace old table =====
# cur.execute("DROP TABLE aya")
# cur.execute("ALTER TABLE aya_new RENAME TO aya")
# print("[INFO] Old aya table replaced.")
#
# # ===== Step 11: Optimize size =====
# conn.commit()
# print("[INFO] Running VACUUM...")
# cur.execute("VACUUM")
# conn.close()
#
# print("\n✅ Done! New DB saved at:", OUTPUT_DB_PATH)
import sqlite3
import shutil
import os

# ===== Paths =====
DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran.sqlite"
OUTPUT_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quran_reordered.sqlite"

# ===== Step 1: Backup original DB =====
shutil.copy(DB_PATH, OUTPUT_DB_PATH)
print(f"Copied database to: {OUTPUT_DB_PATH}")

conn = sqlite3.connect(OUTPUT_DB_PATH)
cur = conn.cursor()

# ===== Step 2: Get columns and types from PRAGMA =====
cur.execute("PRAGMA table_info(aya)")
columns_info = cur.fetchall()

col_names = [col[1] for col in columns_info]
col_types = {col[1]: col[2] for col in columns_info}

print("\n[DEBUG] Columns from PRAGMA:", col_names)
print("[DEBUG] Column types from PRAGMA:", col_types)

if "page_indopak" not in col_names:
    raise ValueError("Column 'page_indopak' does not exist in aya table!")

# ===== Step 3: Prepare new column order =====
new_order = col_names.copy()
new_order.remove("page_indopak")
new_order.insert(3, "page_indopak")
print("\n[DEBUG] New column order:", new_order)

# ===== Step 4: Build CREATE TABLE with new order =====
new_col_defs = [f'"{col}" {col_types[col]}' if col_types[col] else f'"{col}"'
                for col in new_order]
create_new_sql = f"CREATE TABLE aya_new ({', '.join(new_col_defs)})"
print("\n[DEBUG] New CREATE TABLE SQL:\n", create_new_sql)

# ===== Step 5: Create new table =====
cur.execute(create_new_sql)

# ===== Step 6: Copy data into new table =====
cols_str = ", ".join(f'"{c}"' for c in new_order)
insert_sql = f"INSERT INTO aya_new ({cols_str}) SELECT {cols_str} FROM aya"
print("\n[DEBUG] Insert SQL:\n", insert_sql)
cur.execute(insert_sql)

print("\n[INFO] Data copied into new table in new order.")

# ===== Step 7: Replace old table =====
cur.execute("DROP TABLE aya")
cur.execute("ALTER TABLE aya_new RENAME TO aya")
print("[INFO] Old table replaced with reordered table.")

# ===== Step 8: Optimize DB size =====
conn.commit()
print("[INFO] Running VACUUM...")
cur.execute("VACUUM")
conn.close()

print("\n✅ Done! New DB saved at:", OUTPUT_DB_PATH)
