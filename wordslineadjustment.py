import sqlite3

DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\MOD\quranpages.sqlite"

# LINE_ENDS for page 3 as provided
LINE_ENDS = {
    3: [
        (2, 6, 2),
        (2, 7, 1),
        (2, 7, 12),
        (2, 8, 7),
        (2, 9, 5),
        (2, 10, 3),
        (2, 10, 14),
        (2, 11, 12),
        (2, 13, 3),
        (2, 13, 15),
        (2, 14, 6),
        (2, 14, 17),
        (2, 16, 1),
        (2, 16, 10),
        (2, 17, 7),
        (2, 17, 18),
    ]
}

def update_lines_for_page(page_num, line_ends):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    prev_end = (2, 0, 0)  # Surah 2, Aya 0, Word 0: starting point before any data

    for line_num, current_end in enumerate(line_ends, start=1):
        sura, aya, word = current_end
        psura, paya, pword = prev_end

        # Build query to update all rows > prev_end and <= current_end
        # The sorting key is (sura, aya, word), so we select rows in that range

        cursor.execute(f"""
            UPDATE ayarects
            SET page = ?, line = ?
            WHERE soraid = ? AND
            (
                (ayaid > ?) OR
                (ayaid = ? AND word > ?)
            )
            AND
            (
                (ayaid < ?) OR
                (ayaid = ? AND word <= ?)
            )
        """, (
            page_num,
            line_num,
            2,             # soraid
            paya, paya, pword,
            aya, aya, word,
        ))

        prev_end = current_end

    conn.commit()
    conn.close()
    print(f"✅ Updated page {page_num} lines successfully.")

if __name__ == "__main__":
    update_lines_for_page(3, LINE_ENDS[3])
