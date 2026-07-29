import os
import re
import json
import sqlite3

# ============================================================
# PATHS
# ============================================================

SOURCE_DB = r"D:\Android & Code Work\Working Code\CIT\HolyQuran-Gwal\on_lang_pack_kurdi\src\main\assets\kurdish_kurmanji_unknown.db"

SORTED_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_sorted.db"

MERGED_DB = r"D:\Android & Code Work\Assets Working\db\translationnewdb\kurmanji_merged.db"

OUTPUT_ROOT = r"D:\Android & Code Work\Assets Working\db\tafseer_reports_4"

OUTPUT_JSON = os.path.join(
    OUTPUT_ROOT,
    "merge_validation_report.json"
)

# ============================================================
# DB CONFIG
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

    # Remove zero-width / RTL chars
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    # Normalize whitespace
    text = " ".join(text.split())

    return text


# ============================================================
# LOAD DATABASE
# ============================================================

def load_db(db_path):

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
# MAIN
# ============================================================

def main():

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    print("Loading source database...")
    source_db = load_db(SOURCE_DB)

    print("Loading sorted database...")
    sorted_db = load_db(SORTED_DB)

    print("Loading merged database...")
    merged_db = load_db(MERGED_DB)

    report = []

    matched_old = 0
    matched_sorted = 0
    not_matched = 0

    total = len(merged_db)

    for (sura, ayah), merged_text in sorted(merged_db.items()):

        source_text = source_db.get((sura, ayah), "")
        sorted_text = sorted_db.get((sura, ayah), "")

        merged_norm = normalize(merged_text)
        source_norm = normalize(source_text)
        sorted_norm = normalize(sorted_text)

        # ----------------------------------------------------
        # Priority 1: Match OLD database
        # ----------------------------------------------------
        if merged_norm == source_norm:

            matched_old += 1

            report.append({
                "soraid": sura,
                "ayaid": ayah,
                "status": "matched_old"
            })

        # ----------------------------------------------------
        # Priority 2: Match SORTED database
        # ----------------------------------------------------
        elif merged_norm == sorted_norm:

            matched_sorted += 1

            report.append({
                "soraid": sura,
                "ayaid": ayah,
                "status": "matched_sorted"
            })

        # ----------------------------------------------------
        # Priority 3: Match neither
        # ----------------------------------------------------
        else:

            not_matched += 1

            report.append({
                "soraid": sura,
                "ayaid": ayah,
                "status": "not_matched",
                "source": source_text,
                "sorted": sorted_text,
                "merged": merged_text
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

    print()
    print("=" * 60)
    print("MERGE VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Total verses   : {total}")
    print(f"Matched OLD    : {matched_old}")
    print(f"Matched SORTED : {matched_sorted}")
    print(f"Not matched    : {not_matched}")
    print()
    print("Report saved:")
    print(OUTPUT_JSON)


if __name__ == "__main__":
    main()