import os
import json
import sqlite3
import re

# ============================================================
# PATHS
# ============================================================

SOURCE_DB = r"D:\Android & Code Work\Working Code\CIT\HolyQuran-Gwal\on_lang_pack_kurdi\src\main\assets\kurdish_kurmanji_unknown.db"

SORTED_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_sorted.db"

OUTPUT_ROOT = r"D:\Android & Code Work\Assets Working\db\tafseer_reports_3"

OUTPUT_JSON = os.path.join(
    OUTPUT_ROOT,
    "missing_or_different.json"
)

# ============================================================
# CONFIG
# ============================================================

TABLE_NAME = "verses"

SOURCE_SURA_COL = "sura"
SOURCE_AYAH_COL = "ayah"
SOURCE_TEXT_COL = "text"

# ============================================================
# HELPERS
# ============================================================

def normalize2(text):
    if text is None:
        return ""

    return " ".join(str(text).split()).strip()

def normalize(text):
    if text is None:
        return ""

    text = str(text)

    # remove zero-width chars
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

    # lowercase
    text = text.lower()

    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    # normalize whitespace
    text = " ".join(text.split())

    return text


def load_db_as_dict(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(f"""
        SELECT
            {SOURCE_SURA_COL},
            {SOURCE_AYAH_COL},
            {SOURCE_TEXT_COL}
        FROM {TABLE_NAME}
    """)

    data = {}

    for sura, ayah, text in cur.fetchall():
        data[(sura, ayah)] = text or ""

    conn.close()

    return data


# ============================================================
# MAIN
# ============================================================

def main():

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    print("Loading source database...")
    source_data = load_db_as_dict(SOURCE_DB)

    print("Loading sorted database...")
    sorted_data = load_db_as_dict(SORTED_DB)

    print()
    print("Source verses :", len(source_data))
    print("Sorted verses :", len(sorted_data))
    print()

    report = []

    missing_count = 0
    different_count = 0

    for (sura, ayah), source_text in sorted(source_data.items()):

        sorted_text = sorted_data.get((sura, ayah))

        # ----------------------------------------------------
        # Missing verse
        # ----------------------------------------------------
        if sorted_text is None:

            missing_count += 1

            report.append({
                "soraid": sura,
                "ayaid": ayah,
                "tafseer": source_text
            })

            continue

        # ----------------------------------------------------
        # Different text
        # ----------------------------------------------------
        if normalize(source_text) != normalize(sorted_text):

            different_count += 1

            report.append({
                "soraid": sura,
                "ayaid": ayah,
                "tafseer": source_text
            })

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("COMPARISON COMPLETE")
    print("=" * 60)
    print(f"Missing verses   : {missing_count}")
    print(f"Different verses : {different_count}")
    print(f"Total reported   : {len(report)}")
    print()
    print("Output:")
    print(OUTPUT_JSON)


if __name__ == "__main__":
    main()