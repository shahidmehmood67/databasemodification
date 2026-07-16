import sqlite3
import json
import traceback

DB_PATH = r"H:\Other Projects\Python\db\quran.sqlite"
JSON_PATH = r"H:\Other Projects\Python\db\juz_markers.json"

TABLE_NAME = "aya"


# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

def log(msg):
    print(msg)


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def add_column_if_missing(cursor, table, column):
    if not column_exists(cursor, table, column):
        log(f"[INFO] Adding column: {column}")
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} INTEGER DEFAULT 0"
        )
    else:
        log(f"[OK] Column already exists: {column}")


def get_rowid(cursor, surah, ayah):
    cursor.execute("""
        SELECT rowid
        FROM aya
        WHERE soraid = ?
          AND ayaid = ?
        LIMIT 1
    """, (surah, ayah))

    row = cursor.fetchone()

    if row is None:
        raise Exception(f"Verse not found: {surah}:{ayah}")

    return row[0]


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

try:

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create columns if needed
    add_column_if_missing(cursor, TABLE_NAME, "quarter_indopak")
    add_column_if_missing(cursor, TABLE_NAME, "quarter_indopak_start")

    conn.commit()

    # Reset previous data
    log("\nResetting previous values...")

    cursor.execute("""
        UPDATE aya
        SET
            quarter_indopak = 0,
            quarter_indopak_start = 0
    """)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_updated = 0

    for juz in range(1, 31):

        key = f"Juz {juz}"

        if key not in data:
            raise Exception(f"{key} not found in JSON")

        markers = data[key]

        start = markers["Start"]
        quarter = markers["Quarter"]
        half = markers["Half"]
        three = markers["ThreeQuarter"]

        start_row = get_rowid(cursor, start["surah"], start["ayah"])
        quarter_row = get_rowid(cursor, quarter["surah"], quarter["ayah"])
        half_row = get_rowid(cursor, half["surah"], half["ayah"])
        three_row = get_rowid(cursor, three["surah"], three["ayah"])

        # Last verse of this juz
        cursor.execute("""
            SELECT rowid
            FROM aya
            WHERE joza = ?
            ORDER BY rowid DESC
            LIMIT 1
        """, (juz,))

        row = cursor.fetchone()

        if row is None:
            raise Exception(f"No verses found for Juz {juz}")

        end_row = row[0]

        log(f"\n==============================")
        log(f"JUZ {juz}")
        log(f"Start          : row {start_row}")
        log(f"Quarter        : row {quarter_row}")
        log(f"Half           : row {half_row}")
        log(f"ThreeQuarter   : row {three_row}")
        log(f"End            : row {end_row}")

        # Part 1
        cursor.execute("""
            UPDATE aya
            SET quarter_indopak = 1
            WHERE rowid >= ?
              AND rowid < ?
        """, (start_row, quarter_row))

        total_updated += cursor.rowcount

        # Part 2
        cursor.execute("""
            UPDATE aya
            SET quarter_indopak = 2
            WHERE rowid >= ?
              AND rowid < ?
        """, (quarter_row, half_row))

        total_updated += cursor.rowcount

        # Part 3
        cursor.execute("""
            UPDATE aya
            SET quarter_indopak = 3
            WHERE rowid >= ?
              AND rowid < ?
        """, (half_row, three_row))

        total_updated += cursor.rowcount

        # Part 4
        cursor.execute("""
            UPDATE aya
            SET quarter_indopak = 4
            WHERE rowid >= ?
              AND rowid <= ?
        """, (three_row, end_row))

        total_updated += cursor.rowcount

        # Start markers
        for r in [start_row, quarter_row, half_row, three_row]:
            cursor.execute("""
                UPDATE aya
                SET quarter_indopak_start = 1
                WHERE rowid = ?
            """, (r,))

    conn.commit()

    log("\n=========================================")
    log("SUCCESS")
    log(f"Total updated rows : {total_updated}")
    log("Database committed successfully.")
    log("=========================================")

except Exception as e:

    print("\n=========================================")
    print("ERROR OCCURRED")
    print("=========================================")
    print(e)
    traceback.print_exc()

    try:
        conn.rollback()
        print("\nDatabase rollback completed.")
    except Exception:
        pass

finally:
    try:
        conn.close()
    except Exception:
        pass