import sqlite3
import os

OLD_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\ORG\quranpages.sqlite"
NEW_DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\MOD\quranpages.sqlite"

PAGE_ENDS = [
    (2, 2, 4, 13),
    (3, 2, 17, 18),
    (4, 2, 25, 24),
    (5, 2, 32, 5),
    (6, 2, 42, 2),
    (7, 2, 54, 13),
    (8, 2, 61, 22),
    (9, 2, 68, 15),
    (10, 2, 76, 4),
    (11, 2, 83, 27),
    (12, 2, 89, 18),
    (13, 2, 96, 25),
    (14, 2, 102, 83),
    (15, 2, 111, 4),
    (16, 2, 118, 20),
    (17, 2, 126, 12),
    (18, 2, 134, 7),
    (19, 2, 141, 18),
]

def fetch_old_data():
    conn = sqlite3.connect(OLD_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT soraid, ayaid, word, page, line, minx, maxx, miny, maxy
        FROM ayarects
        ORDER BY soraid, ayaid, word
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def remap_pages(old_data, page_ends):
    new_data = []
    page_index = 0
    current_new_page, end_sura, end_aya, end_word = page_ends[page_index]
    current_line = 1

    for sura, aya, word, old_page, old_line, minx, maxx, miny, maxy in old_data:
        new_data.append((sura, aya, word, current_new_page, current_line, minx, maxx, miny, maxy))

        if (sura, aya, word) == (end_sura, end_aya, end_word):
            print(f"📄 Page {current_new_page} ends at {sura}:{aya} word {word} (line {current_line})")
            page_index += 1
            if page_index < len(page_ends):
                current_new_page, end_sura, end_aya, end_word = page_ends[page_index]
                current_line = 1
            else:
                break
        else:
            current_line += 1
            if current_line > 16:
                current_line = 16
    return new_data

def save_new_data(new_data):
    conn = sqlite3.connect(NEW_DB_PATH)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayarects (
            soraid INTEGER,
            ayaid INTEGER,
            word INTEGER,
            page INTEGER,
            line INTEGER,
            minx REAL,
            maxx REAL,
            miny REAL,
            maxy REAL,
            PRIMARY KEY (soraid, ayaid, word)
        )
    """)

    # Clear old data (avoids UNIQUE constraint errors)
    cursor.execute("DELETE FROM ayarects")

    # Insert fresh data
    cursor.executemany("""
        INSERT INTO ayarects (soraid, ayaid, word, page, line, minx, maxx, miny, maxy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, new_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if not os.path.exists(OLD_DB_PATH):
        raise FileNotFoundError(f"Old DB not found at {OLD_DB_PATH}")
    if not os.path.exists(NEW_DB_PATH):
        raise FileNotFoundError(f"New DB not found at {NEW_DB_PATH}")

    old_data = fetch_old_data()
    new_data = remap_pages(old_data, PAGE_ENDS)
    save_new_data(new_data)
    print(f"✅ Mapping complete. {len(new_data)} records processed.")
