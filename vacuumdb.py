import sqlite3
import os

# Hardcoded DB path
db_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\MOD\New folder\quranpages.sqlite"

if not os.path.exists(db_path):
    print(f"❌ File not found: {db_path}")
else:
    before_size = os.path.getsize(db_path) / 1024
    print(f"Before VACUUM: {before_size:.2f} KB")

    con = sqlite3.connect(db_path)
    con.execute("VACUUM;")  # Rebuild DB without empty pages
    con.close()

    after_size = os.path.getsize(db_path) / 1024
    print(f"After VACUUM:  {after_size:.2f} KB")
    print(f"✅ Reduced by: {before_size - after_size:.2f} KB")
