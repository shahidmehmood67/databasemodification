import sqlite3

DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"

def update_page4_minmax():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Predefined miny and maxy values for lines 1 to 16
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
            SET minx = 55,
                maxx = 850,
                miny = ?,
                maxy = ?
            WHERE page = 4 AND line = ?
        """, (miny, maxy, line_no))

        print(f"Updated page 4, line {line_no} with miny={miny}, maxy={maxy}")

    conn.commit()
    conn.close()
    print("✅ Page 4 minx, maxx, miny, maxy updated successfully.")

if __name__ == "__main__":
    update_page4_minmax()
