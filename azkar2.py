import json
import sqlite3
from pathlib import Path

# =========================
# Configuration
# =========================
DB_PATH = r"H:\Other Projects\Python\db\hisnul.sqlite3"
JSON_FOLDER = Path(r"H:\Other Projects\Python\db\translatedazkar")

# Do NOT include English & Arabic (already exist)
LANGUAGES = {
    "spanish": "es",
    "portuguese": "pt",
    "french": "fr",
    "german": "de",
    "russian": "ru",
    "uzbek": "uz",
    "amharic": "am",
    "hindi": "hi",
    "italian": "it",
    "persian": "fa",
    "turkish": "tr",
    "urdu": "ur",
    "bangla": "bn",
    "hausa": "ha",
    "indonesian": "id",
    "malay": "ms",
    "somali": "so",
}

TABLE_NAME = "dua_group"
ID_COLUMN = "_id"

# =========================
# Connect
# =========================
print("=" * 60)
print("Opening database...")
print(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# Read existing columns
# =========================
cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
existing_columns = {row[1] for row in cursor.fetchall()}

print(f"\nFound {len(existing_columns)} existing columns.")
print(existing_columns)

total_languages = 0
total_updated = 0

print("\n" + "=" * 60)

# =========================
# Process each language
# =========================
for language_name, language_code in LANGUAGES.items():

    column_name = f"{language_code}_title"
    json_file = JSON_FOLDER / f"{language_name}.json"

    print(f"\nProcessing: {language_name}")

    # -------------------------
    # Check JSON file
    # -------------------------
    if not json_file.exists():
        print(f"  [SKIP] File not found: {json_file.name}")
        continue

    # -------------------------
    # Create column if needed
    # -------------------------
    if column_name not in existing_columns:
        print(f"  [+] Creating column: {column_name}")
        cursor.execute(
            f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} TEXT"
        )
        existing_columns.add(column_name)
    else:
        print(f"  [OK] Column already exists: {column_name}")

    # -------------------------
    # Load JSON
    # -------------------------
    with open(json_file, "r", encoding="utf-8") as f:
        translations = json.load(f)

    print(f"  Loaded {len(translations)} translations")

    # -------------------------
    # Update database
    # -------------------------
    updated = 0

    for dua_id, title in translations.items():
        cursor.execute(
            f"""
            UPDATE {TABLE_NAME}
            SET {column_name} = ?
            WHERE {ID_COLUMN} = ?
            """,
            (title, int(dua_id)),
        )

        updated += cursor.rowcount

    print(f"  Updated {updated} rows.")

    total_languages += 1
    total_updated += updated

# =========================
# Save
# =========================
print("\n" + "=" * 60)
print("Saving changes...")

conn.commit()
conn.close()

print("Done!")
print(f"Languages imported : {total_languages}")
print(f"Rows updated       : {total_updated}")
print("=" * 60)