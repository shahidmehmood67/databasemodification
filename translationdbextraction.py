import os
import sqlite3
import json
import re

# Root containing language packs
ROOT_DIR = r"H:\CodersInsightWorkSpace\Gwal Apps\Al Quran\Quran"

# Output folder
OUTPUT_ROOT = r"H:\Other Projects\Python\db\tafseer_reports"

# Regex patterns
REFERENCE_ONLY = re.compile(r'^\s*\d+\s*:\s*\d+\s*$')
HTML_ENTITY = re.compile(r'&[A-Za-z#0-9]+;')

os.makedirs(OUTPUT_ROOT, exist_ok=True)

total_languages = 0
total_databases = 0
total_bad_rows = 0

print("=" * 80)
print("Scanning language packs...")
print("=" * 80)

for folder in sorted(os.listdir(ROOT_DIR)):
    if not folder.startswith("on_lang_pack_"):
        continue

    total_languages += 1

    assets_path = os.path.join(
        ROOT_DIR,
        folder,
        "src",
        "main",
        "assets"
    )

    if not os.path.isdir(assets_path):
        print(f"[Missing Assets] {folder}")
        continue

    output_lang_dir = os.path.join(OUTPUT_ROOT, folder)
    os.makedirs(output_lang_dir, exist_ok=True)

    print(f"\nLanguage: {folder}")

    sqlite_files = [
        f for f in os.listdir(assets_path)
        if f.lower().endswith(".sqlite")
    ]

    if not sqlite_files:
        print("   No sqlite databases found.")
        continue

    for db_name in sorted(sqlite_files):

        db_path = os.path.join(assets_path, db_name)
        total_databases += 1

        print(f"   Checking {db_name}")

        bad_rows = []

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            cur.execute("""
                SELECT soraid, ayaid, tafseer
                FROM ayatafseer
            """)

            for soraid, ayaid, tafseer in cur.fetchall():

                bad = False

                if tafseer is None:
                    bad = True
                    tafseer = ""

                text = str(tafseer).strip()

                if text == "":
                    bad = True

                if len(text) <= 5:
                    bad = True

                if "&quot;" in text:
                    bad = True

                if HTML_ENTITY.search(text):
                    bad = True

                if REFERENCE_ONLY.fullmatch(text):
                    bad = True

                if bad:
                    bad_rows.append({
                        "soraid": soraid,
                        "ayaid": ayaid,
                        "tafseer": tafseer
                    })

            conn.close()

        except Exception as e:
            print(f"      ERROR: {e}")
            continue

        json_name = os.path.splitext(db_name)[0] + ".json"
        json_path = os.path.join(output_lang_dir, json_name)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                bad_rows,
                f,
                ensure_ascii=False,
                indent=2
            )

        total_bad_rows += len(bad_rows)

        print(f"      -> {len(bad_rows)} suspicious rows")

print("\n" + "=" * 80)
print("Finished")
print("=" * 80)
print(f"Languages scanned : {total_languages}")
print(f"Databases scanned : {total_databases}")
print(f"Suspicious rows   : {total_bad_rows}")
print(f"Output folder     : {OUTPUT_ROOT}")