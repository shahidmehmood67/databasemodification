import sqlite3


FOLDER_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\quran.sqlite"
def fix_page_indopak(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all distinct soraids
    cursor.execute("SELECT DISTINCT soraid FROM aya")
    sora_ids = [row[0] for row in cursor.fetchall()]

    for soraid in sora_ids:
        # Get page_indopak of ayaid = 1
        cursor.execute("SELECT page_indopak FROM aya WHERE soraid = ? AND ayaid = 1", (soraid,))
        row = cursor.fetchone()

        if row:
            page_indopak_aya1 = row[0]

            # Update ayaid = 0 with this value
            cursor.execute(
                "UPDATE aya SET page_indopak = ? WHERE soraid = ? AND ayaid = 0",
                (page_indopak_aya1, soraid)
            )
            print(f"Updated soraid={soraid}: ayaid=0 -> page_indopak={page_indopak_aya1}")

    conn.commit()
    conn.close()

# Example usage
if __name__ == "__main__":
    fix_page_indopak(FOLDER_PATH)  # replace with your database path
