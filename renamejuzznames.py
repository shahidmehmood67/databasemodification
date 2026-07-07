import sqlite3
import os
import sys

# ==============================================================================
# Configuration
# ==============================================================================

DB_PATH = r"H:\Other Projects\Python\db\quran.sqlite"

# ==============================================================================
# Correct English Juz Names
# ==============================================================================

ENGLISH_NAMES = [
    "Alif Lam Meem",  # 1
    "Sayaqool",  # 2
    "Tilkal Rusulu",  # 3
    "Lan Tanaloo",  # 4
    "Wal Mohsanatu",  # 5
    "La Yuhibbullah",  # 6
    "Wa Iza Samiu",  # 7
    "Wa Lau Annana",  # 8
    "Qalal Malao",  # 9
    "Wa A'lamu",  # 10
    "Yatazeroon",  # 11
    "Wa Mamin Da'abatin",  # 12
    "Wa Ma Ubrioo",  # 13
    "Rubama",  # 14
    "Subhanalladhi",  # 15
    "Qala Alam",  # 16
    "Iqtaraba",  # 17
    "Qadd Aflaha",  # 18
    "Wa Qala illadhina",  # 19
    "A'man Khalaqa",  # 20
    "Utlu Ma Oohiya",  # 21
    "Wa Manyaqnut",  # 22
    "Wa Mali",  # 23
    "Faman Azlamu",  # 24
    "Ilayhi Yuruddu",  # 25
    "Ha Meem",  # 26
    "Qala Fama Khatbukum",  # 27
    "Qadd Sami Allah",  # 28
    "Tabaraka lladhi",  # 29
    "Amma"  # 30
]


# ==============================================================================
# Main
# ==============================================================================

def main():
    print("=" * 70)
    print("Quran Juz Table - Update English Names Only")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found:\n{DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"✓ Connected to: {DB_PATH}")

    updated = 0

    print("\nUpdating English names in 'juz' table...\n")

    for juzid in range(1, 31):
        english_name = ENGLISH_NAMES[juzid - 1]

        cursor.execute("""
            UPDATE juz 
            SET name_english = ? 
            WHERE juzid = ?
        """, (english_name, juzid))

        if cursor.rowcount > 0:
            print(f"✓ Juz {juzid:2d} → {english_name}")
            updated += 1
        else:
            print(f"⚠ Juz {juzid:2d} not found in table")

    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("Update Completed!")
    print("=" * 70)
    print(f"Total Juz updated : {updated}/30")

    if updated == 30:
        print("🎉 All English names updated successfully!")
    else:
        print("⚠ Some Juz were not updated.")


if __name__ == "__main__":
    main()