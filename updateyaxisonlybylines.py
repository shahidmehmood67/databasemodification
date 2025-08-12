import sqlite3

DB_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\MOD\quranpages.sqlite"
def update_page3_minmax_y_only():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Replace these with correct miny and maxy values for page 3 lines
    miny_values = [
        75, 160, 245, 330, 415, 500, 585, 670,
        755, 840, 925, 1010, 1095, 1180, 1265, 1350
    ]

    maxy_values = [
        150, 235, 320, 405, 490, 575, 660, 745,
        830, 915, 1000, 1085, 1170, 1255, 1340, 1425
    ]

    for line_no in range(1, 17):
        miny = miny_values[line_no - 1]
        maxy = maxy_values[line_no - 1]

        cur.execute("""
            UPDATE ayarects
            SET miny = ?, maxy = ?
            WHERE page = 3 AND line = ?
        """, (miny, maxy, line_no))

        print(f"Updated page 3, line {line_no} with miny={miny}, maxy={maxy}")

    conn.commit()
    conn.close()
    print("✅ Page 3 miny and maxy updated successfully.")

if __name__ == "__main__":
    update_page3_minmax_y_only()
