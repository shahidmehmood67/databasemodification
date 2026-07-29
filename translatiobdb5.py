import sqlite3
import shutil
import os

# ---------------------------------------------------------
# Database paths
# ---------------------------------------------------------

SOURCE_DB = r"H:\Other Projects\Python\db\quranV3.sqlite"
OUTPUT_DB = r"H:\Other Projects\Python\db\quranV4.sqlite"


# ---------------------------------------------------------
# Check source database
# ---------------------------------------------------------

if not os.path.exists(SOURCE_DB):
    raise FileNotFoundError(
        f"Source database not found:\n{SOURCE_DB}"
    )


# ---------------------------------------------------------
# Remove old quranV4 if it already exists
# ---------------------------------------------------------

if os.path.exists(OUTPUT_DB):
    os.remove(OUTPUT_DB)


# ---------------------------------------------------------
# Copy quranV3 -> quranV4
# ---------------------------------------------------------

print("Creating quranV4.sqlite...")

shutil.copy2(SOURCE_DB, OUTPUT_DB)

print(f"Created: {OUTPUT_DB}")


# ---------------------------------------------------------
# Open quranV4 database
# ---------------------------------------------------------

conn = sqlite3.connect(OUTPUT_DB)
cursor = conn.cursor()


# ---------------------------------------------------------
# Read all Surah names
# ---------------------------------------------------------

cursor.execute("""
    SELECT rowid, name_english
    FROM sora
    WHERE name_english IS NOT NULL
""")

rows = cursor.fetchall()


# ---------------------------------------------------------
# Update only names starting with "Surat "
# ---------------------------------------------------------

updated_count = 0

for rowid, name_english in rows:

    # Only remove "Surat " if it is at the beginning
    if name_english.startswith("Surat "):

        new_name = name_english[len("Surat "):]

        cursor.execute("""
            UPDATE sora
            SET name_english = ?
            WHERE rowid = ?
        """, (new_name, rowid))

        print(f"{name_english} -> {new_name}")

        updated_count += 1


# ---------------------------------------------------------
# Save changes
# ---------------------------------------------------------

conn.commit()


# ---------------------------------------------------------
# Close database
# ---------------------------------------------------------

conn.close()


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------

print()
print("========================================")
print("Database update completed successfully")
print("========================================")
print(f"Updated Surah names: {updated_count}")
print(f"Output database: {OUTPUT_DB}")