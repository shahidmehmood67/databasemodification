import sqlite3
import json
import os
import sys

# ==============================================================================
# Configuration
# ==============================================================================

DB_PATH = r"H:\Other Projects\Python\db\quran.sqlite"

JSON_PATH = r"H:\CodersInsightWorkSpace\Daily Life\Quran\Quran Daily Life\app\src\main\assets\quran_meta.json"


# ==============================================================================
# Helper
# ==============================================================================

def log(message):
    print(message)


# ==============================================================================
# Main
# ==============================================================================

def main():

    log("=" * 70)
    log("Quran Juz Table Generator")
    log("=" * 70)

    # --------------------------------------------------------------------------
    # Check files
    # --------------------------------------------------------------------------

    if not os.path.exists(DB_PATH):
        log(f"❌ Database not found:\n{DB_PATH}")
        sys.exit(1)

    if not os.path.exists(JSON_PATH):
        log(f"❌ JSON not found:\n{JSON_PATH}")
        sys.exit(1)

    log(f"✓ Database : {DB_PATH}")
    log(f"✓ JSON      : {JSON_PATH}")

    # --------------------------------------------------------------------------
    # Load JSON
    # --------------------------------------------------------------------------

    log("\nLoading JSON...")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    juzs = meta.get("juzs", [])

    log(f"✓ Loaded {len(juzs)} Juz entries")

    if len(juzs) != 30:
        raise Exception(f"Expected 30 Juz entries, found {len(juzs)}")

    # --------------------------------------------------------------------------
    # Open database
    # --------------------------------------------------------------------------

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    log("\nConnected to database.")

    # --------------------------------------------------------------------------
    # Create table
    # --------------------------------------------------------------------------

    log("\nCreating table if it doesn't exist...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS juz(
        juzid INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        name_english TEXT NOT NULL,
        starting_page INTEGER NOT NULL,
        starting_page_indopak INTEGER NOT NULL
    )
    """)

    conn.commit()

    log("✓ Table ready.")

    # --------------------------------------------------------------------------
    # Clear previous data
    # --------------------------------------------------------------------------

    log("Clearing previous records...")

    cursor.execute("DELETE FROM juz")

    conn.commit()

    log("✓ Previous records removed.")

    # --------------------------------------------------------------------------
    # Insert Data
    # --------------------------------------------------------------------------

    inserted = 0

    log("\n" + "=" * 70)
    log("Processing Juz")
    log("=" * 70)

    for juz in juzs:

        juzid = juz["index"]
        arabic = juz["name"]["ar"]
        english = juz["name"]["en"]

        log(f"\nJuz {juzid}")

        # Find first verse of this juz
        cursor.execute("""
            SELECT
                soraid,
                ayaid,
                page,
                page_indopak
            FROM aya
            WHERE joza = ?
            ORDER BY soraid ASC, ayaid ASC
            LIMIT 1
        """, (juzid,))

        row = cursor.fetchone()

        if row is None:
            log(f"❌ No verse found for Juz {juzid}")
            continue

        soraid, ayaid, page, page_indopak = row

        log(f"  Arabic Name : {arabic}")
        log(f"  English Name: {english}")
        log(f"  Starts From : Surah {soraid}, Ayah {ayaid}")
        log(f"  Page        : {page}")
        log(f"  IndoPak Page: {page_indopak}")

        cursor.execute("""
            INSERT INTO juz(
                juzid,
                name,
                name_english,
                starting_page,
                starting_page_indopak
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            juzid,
            arabic,
            english,
            page,
            page_indopak
        ))

        inserted += 1

        log("  ✓ Inserted")

    # --------------------------------------------------------------------------
    # Commit
    # --------------------------------------------------------------------------

    conn.commit()

    # --------------------------------------------------------------------------
    # Verification
    # --------------------------------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM juz")
    count = cursor.fetchone()[0]

    log("\n" + "=" * 70)
    log("Verification")
    log("=" * 70)

    log(f"Inserted during run : {inserted}")
    log(f"Rows in table       : {count}")

    if count == 30:
        log("\n🎉 SUCCESS!")
        log("All 30 Juz records inserted successfully.")
    else:
        log("\n⚠ WARNING")
        log("Expected 30 rows.")

    conn.close()

    log("\nDatabase connection closed.")


if __name__ == "__main__":
    main()