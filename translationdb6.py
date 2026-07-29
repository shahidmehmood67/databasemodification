import sqlite3
import os
import shutil

# =========================================================
# Source Database
# =========================================================

SOURCE_DB = r"E:\QuranSqlAllData\DB New Translations\selected\old db\kurdish_kurmanji_unknown.sqlite"

# Your original/source table
SOURCE_TABLE = "ayatafseer"

SOURCE_SURA_COLUMN = "soraid"
SOURCE_AYAH_COLUMN = "ayaid"
SOURCE_TEXT_COLUMN = "tafseer"


# =========================================================
# Output Database
# =========================================================

OUTPUT_DIR = r"H:\Other Projects\Python\db\tafseer_newdb2"

OUTPUT_TABLE = "verses"

OUTPUT_SURA_COLUMN = "sura"
OUTPUT_AYAH_COLUMN = "ayah"
OUTPUT_TEXT_COLUMN = "text"


# =========================================================
# Create output directory
# =========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# Keep the same database filename
# =========================================================

OUTPUT_DB = os.path.join(
    OUTPUT_DIR,
    "kurdish_kurmanji_unknown.db"
)


# =========================================================
# Remove existing output database
# =========================================================

if os.path.exists(OUTPUT_DB):
    os.remove(OUTPUT_DB)


# =========================================================
# Check source database
# =========================================================

if not os.path.exists(SOURCE_DB):
    raise FileNotFoundError(
        f"Source database not found:\n{SOURCE_DB}"
    )


print("========================================")
print("DATABASE CONVERSION STARTED")
print("========================================")

print(f"Source DB: {SOURCE_DB}")
print(f"Output DB: {OUTPUT_DB}")


# =========================================================
# Connect to source database
# =========================================================

source_conn = sqlite3.connect(SOURCE_DB)
source_cursor = source_conn.cursor()


# =========================================================
# Read source data
# =========================================================

print()
print("Reading source data...")

source_cursor.execute(f"""
    SELECT
        {SOURCE_SURA_COLUMN},
        {SOURCE_AYAH_COLUMN},
        {SOURCE_TEXT_COLUMN}
    FROM {SOURCE_TABLE}
""")

rows = source_cursor.fetchall()

print(f"Found {len(rows)} records.")


# =========================================================
# Close source database
# =========================================================

source_conn.close()


# =========================================================
# Create output database
# =========================================================

output_conn = sqlite3.connect(OUTPUT_DB)
output_cursor = output_conn.cursor()


# =========================================================
# Create new table
# =========================================================

print()
print(f"Creating table: {OUTPUT_TABLE}")

output_cursor.execute(f"""
    CREATE TABLE {OUTPUT_TABLE} (
        {OUTPUT_SURA_COLUMN} INTEGER NOT NULL,
        {OUTPUT_AYAH_COLUMN} INTEGER NOT NULL,
        {OUTPUT_TEXT_COLUMN} TEXT
    )
""")


# =========================================================
# Insert converted data
# =========================================================

print("Inserting converted data...")

output_cursor.executemany(
    f"""
    INSERT INTO {OUTPUT_TABLE} (
        {OUTPUT_SURA_COLUMN},
        {OUTPUT_AYAH_COLUMN},
        {OUTPUT_TEXT_COLUMN}
    )
    VALUES (?, ?, ?)
    """,
    rows
)


# =========================================================
# Commit changes
# =========================================================

output_conn.commit()


# =========================================================
# Verify inserted records
# =========================================================

output_cursor.execute(
    f"SELECT COUNT(*) FROM {OUTPUT_TABLE}"
)

inserted_count = output_cursor.fetchone()[0]


# =========================================================
# Close output database
# =========================================================

output_conn.close()


# =========================================================
# Final result
# =========================================================

print()
print("========================================")
print("DATABASE CONVERSION COMPLETED")
print("========================================")

print(f"Source records : {len(rows)}")
print(f"Inserted records: {inserted_count}")
print(f"Output database : {OUTPUT_DB}")
print(f"Output table    : {OUTPUT_TABLE}")