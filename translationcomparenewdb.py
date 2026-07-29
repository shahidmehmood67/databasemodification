import os
import re
import sqlite3

# ============================================================
# PATHS
# ============================================================

SOURCE_DB = r"D:\Android & Code Work\Working Code\CIT\HolyQuran-Gwal\on_lang_pack_kurdi\src\main\assets\kurdish_kurmanji_unknown.db"

SCRAPED_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_sorted.db"

OUTPUT_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_merged.db"

# ============================================================
# TABLE CONFIG
# ============================================================

TABLE_NAME = "verses"

SURA_COL = "sura"
AYAH_COL = "ayah"
TEXT_COL = "text"

# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):
    if text is None:
        return ""

    text = str(text)

    # remove zero-width / RTL marks
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

    # lowercase
    text = text.lower()

    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    # normalize whitespace
    text = " ".join(text.split())

    return text


# ============================================================
# LOAD DATABASE
# ============================================================

def load_database(db_path):

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(f"""
        SELECT
            {SURA_COL},
            {AYAH_COL},
            {TEXT_COL}
        FROM {TABLE_NAME}
    """)

    data = {}

    for sura, ayah, text in cur.fetchall():
        data[(sura, ayah)] = text or ""

    conn.close()

    return data


# ============================================================
# CREATE OUTPUT DATABASE
# ============================================================

def create_output_database():

    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)

    conn = sqlite3.connect(OUTPUT_DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE verses (
            sura INTEGER NOT NULL,
            ayah INTEGER NOT NULL,
            text TEXT,
            PRIMARY KEY (sura, ayah)
        )
    """)

    conn.commit()

    return conn


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading source database...")
    source_data = load_database(SOURCE_DB)

    print("Loading scraped database...")
    scraped_data = load_database(SCRAPED_DB)

    print()
    print("Source verses :", len(source_data))
    print("Scraped verses:", len(scraped_data))
    print()

    output_conn = create_output_database()
    output_cur = output_conn.cursor()

    source_preferred = 0
    source_longer = 0
    scraped_longer = 0
    missing_in_scraped = 0

    all_keys = sorted(source_data.keys())

    for sura, ayah in all_keys:

        source_text = source_data.get((sura, ayah), "")
        scraped_text = scraped_data.get((sura, ayah), "")

        # ----------------------------------------------------
        # Missing from scraped DB
        # ----------------------------------------------------
        if not scraped_text:

            final_text = source_text
            missing_in_scraped += 1

        else:

            source_norm = normalize(source_text)
            scraped_norm = normalize(scraped_text)

            # ------------------------------------------------
            # Same text after normalization
            # Prefer OLD database
            # ------------------------------------------------
            if source_norm == scraped_norm:

                final_text = source_text
                source_preferred += 1

            # ------------------------------------------------
            # Different text
            # Choose longer version
            # ------------------------------------------------
            else:

                if len(source_text) >= len(scraped_text):
                    final_text = source_text
                    source_longer += 1
                else:
                    final_text = scraped_text
                    scraped_longer += 1

        output_cur.execute("""
            INSERT INTO verses
            (sura, ayah, text)
            VALUES (?, ?, ?)
        """, (
            sura,
            ayah,
            final_text
        ))

    output_conn.commit()
    output_conn.close()

    print("=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)
    print()
    print("Same after normalization")
    print("→ Preferred source DB :", source_preferred)
    print()
    print("Different text")
    print("→ Source longer       :", source_longer)
    print("→ Scraped longer      :", scraped_longer)
    print()
    print("Missing in scraped DB :", missing_in_scraped)
    print()
    print("Output:")
    print(OUTPUT_DB)


if __name__ == "__main__":
    main()