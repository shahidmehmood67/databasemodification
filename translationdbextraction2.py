import os
import sqlite3
import json
import re


# ============================================================
# CONFIGURATION
# ============================================================

# Root containing language packs
# ROOT_DIR = r"H:\Other Projects\Python\db\tafseer_newdb"
ROOT_DIR = r"D:\Android & Code Work\Working Code\CIT\HolyQuran-Gwal"

# Output folder
# OUTPUT_ROOT = r"H:\Other Projects\Python\db\tafseer_reports_3_newdb_2"
OUTPUT_ROOT = r"D:\Android & Code Work\Assets Working\db\tafseer_reports"



# ============================================================
# QURAN.COM DATABASE SCHEMA
# ============================================================

QURAN_COM_TABLE = "verses"

QURAN_COM_SURA_COLUMN = "sura"
QURAN_COM_AYAH_COLUMN = "ayah"
QURAN_COM_TEXT_COLUMN = "text"


# ============================================================
# REGEX PATTERNS
# ============================================================

REFERENCE_ONLY = re.compile(
    r'^\s*\d+\s*:\s*\d+\s*$'
)

HTML_ENTITY = re.compile(
    r'&[A-Za-z#0-9]+;'
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_ROOT,
    exist_ok=True
)


# ============================================================
# COUNTERS
# ============================================================

total_languages = 0
total_databases = 0
total_bad_rows = 0


# ============================================================
# START
# ============================================================

print("=" * 80)
print("Scanning language packs...")
print("=" * 80)


# ============================================================
# SCAN LANGUAGE PACKS
# ============================================================

for folder in sorted(os.listdir(ROOT_DIR)):

    # Only process language pack folders
    if not folder.startswith("on_lang_pack_"):
        continue

    total_languages += 1

    if folder == "on_lang_pack_kurdi":
        continue

    # Database files are directly inside the language folder
    # language_path = os.path.join(
    #     ROOT_DIR,
    #     folder
    # )

    language_path = os.path.join(
        ROOT_DIR,
        folder,
        "src",
        "main",
        "assets"
    )

    if not os.path.isdir(language_path):
        print(
            f"[Missing Folder] {folder}"
        )
        continue


    # ========================================================
    # CREATE OUTPUT LANGUAGE FOLDER
    # ========================================================

    output_lang_dir = os.path.join(
        OUTPUT_ROOT,
        folder
    )

    os.makedirs(
        output_lang_dir,
        exist_ok=True
    )


    print(
        f"\nLanguage: {folder}"
    )


    # ========================================================
    # FIND .DB DATABASE FILES
    # ========================================================

    db_files = [
        f
        for f in os.listdir(language_path)
        if f.lower().endswith(".db")
    ]


    if not db_files:
        print(
            "   No .db databases found."
        )
        continue


    # ========================================================
    # PROCESS EACH DATABASE
    # ========================================================

    for db_name in sorted(db_files):

        db_path = os.path.join(
            language_path,
            db_name
        )

        total_databases += 1

        print(
            f"   Checking {db_name}"
        )


        # List of suspicious rows
        bad_rows = []


        # ====================================================
        # CONNECT TO DATABASE
        # ====================================================

        try:

            conn = sqlite3.connect(
                db_path
            )

            cur = conn.cursor()


            # =================================================
            # READ VERSES
            # =================================================

            cur.execute(
                f"""
                SELECT
                    {QURAN_COM_SURA_COLUMN},
                    {QURAN_COM_AYAH_COLUMN},
                    {QURAN_COM_TEXT_COLUMN}
                FROM {QURAN_COM_TABLE}
                """
            )


            # =================================================
            # CHECK EACH ROW
            # =================================================

            for soraid, ayaid, tafseer in cur.fetchall():

                bad = False


                # ---------------------------------------------
                # NULL TEXT
                # ---------------------------------------------

                if tafseer is None:

                    bad = True

                    tafseer = ""


                # ---------------------------------------------
                # CLEAN TEXT
                # ---------------------------------------------

                text = str(
                    tafseer
                ).strip()


                # ---------------------------------------------
                # EMPTY TEXT
                # ---------------------------------------------

                if text == "":

                    bad = True


                # ---------------------------------------------
                # VERY SHORT TEXT
                # ---------------------------------------------

                if len(text) <= 5:

                    bad = True


                # ---------------------------------------------
                # QUOT ENTITY
                # ---------------------------------------------

                if "&quot;" in text:

                    bad = True


                # ---------------------------------------------
                # ANY HTML ENTITY
                # ---------------------------------------------

                if HTML_ENTITY.search(text):

                    bad = True


                # ---------------------------------------------
                # REFERENCE ONLY
                #
                # Example:
                # 2:255
                # ---------------------------------------------

                if REFERENCE_ONLY.fullmatch(text):

                    bad = True


                # ---------------------------------------------
                # SAVE SUSPICIOUS ROW
                # ---------------------------------------------

                if bad:

                    bad_rows.append(
                        {
                            "soraid": soraid,
                            "ayaid": ayaid,
                            "tafseer": tafseer
                        }
                    )


            # =================================================
            # CLOSE DATABASE
            # =================================================

            conn.close()


        except Exception as e:

            print(
                f"      ERROR: {e}"
            )

            continue


        # ====================================================
        # CREATE JSON FILE NAME
        # ====================================================

        json_name = (
            os.path.splitext(db_name)[0]
            + ".json"
        )


        json_path = os.path.join(
            output_lang_dir,
            json_name
        )


        # ====================================================
        # WRITE SUSPICIOUS ROWS TO JSON
        # ====================================================

        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                bad_rows,
                f,
                ensure_ascii=False,
                indent=2
            )


        # ====================================================
        # UPDATE COUNTER
        # ====================================================

        total_bad_rows += len(
            bad_rows
        )


        print(
            f"      -> {len(bad_rows)} suspicious rows"
        )


# ============================================================
# FINISHED
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "Finished"
)

print(
    "=" * 80
)

print(
    f"Languages scanned : {total_languages}"
)

print(
    f"Databases scanned : {total_databases}"
)

print(
    f"Suspicious rows   : {total_bad_rows}"
)

print(
    f"Output folder     : {OUTPUT_ROOT}"
)