import os
import shutil
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

# Existing HolyQuran-Gwal project
ROOT_DIR = r"H:\CodersInsightWorkSpace\Gwal Apps\Al Quran\HolyQuran-Gwal"

# New database source
NEW_DB_ROOT = r"H:\Other Projects\Python\db\tafseer_newdb"

# Log file
LOG_FILE = r"H:\Other Projects\Python\db\tafseer_newdb_replacement.log"


# ============================================================
# LOGGING
# ============================================================

def log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_message = (
        f"{timestamp} | {message}"
    )

    print(log_message)

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            log_message + "\n"
        )


# ============================================================
# COUNTERS
# ============================================================

total_languages = 0
successful_languages = 0
failed_languages = 0

total_deleted_files = 0
total_copied_files = 0


# ============================================================
# START
# ============================================================

# Clear/create log file
with open(
    LOG_FILE,
    "w",
    encoding="utf-8"
) as f:
    f.write("")


log("=" * 80)
log("TAFSEER DATABASE REPLACEMENT STARTED")
log("=" * 80)

log(
    f"Project Root : {ROOT_DIR}"
)

log(
    f"New DB Root  : {NEW_DB_ROOT}"
)

log(
    f"Log File     : {LOG_FILE}"
)

log("=" * 80)


# ============================================================
# VALIDATE ROOT DIRECTORIES
# ============================================================

if not os.path.isdir(ROOT_DIR):

    log(
        f"ERROR: Project root does not exist: {ROOT_DIR}"
    )

    raise SystemExit(1)


if not os.path.isdir(NEW_DB_ROOT):

    log(
        f"ERROR: New DB root does not exist: {NEW_DB_ROOT}"
    )

    raise SystemExit(1)


# ============================================================
# GET LANGUAGE PACK FOLDERS
# ============================================================

language_folders = [
    folder
    for folder in sorted(
        os.listdir(ROOT_DIR)
    )
    if folder.startswith("on_lang_pack_")
    and os.path.isdir(
        os.path.join(
            ROOT_DIR,
            folder
        )
    )
]


log(
    f"Found {len(language_folders)} language pack folders."
)

log("=" * 80)


# ============================================================
# PROCESS EACH LANGUAGE
# ============================================================

for folder in language_folders:

    total_languages += 1

    log("")
    log("-" * 80)
    log(
        f"PROCESSING LANGUAGE: {folder}"
    )
    log("-" * 80)


    # ========================================================
    # EXISTING LANGUAGE PACK
    # ========================================================

    language_path = os.path.join(
        ROOT_DIR,
        folder
    )


    # Destination assets folder
    assets_path = os.path.join(
        language_path,
        "src",
        "main",
        "assets"
    )


    # ========================================================
    # NEW DATABASE SOURCE
    # ========================================================

    new_db_language_path = os.path.join(
        NEW_DB_ROOT,
        folder
    )


    log(
        f"Destination Assets: {assets_path}"
    )

    log(
        f"New DB Source     : {new_db_language_path}"
    )


    # ========================================================
    # CHECK SOURCE LANGUAGE FOLDER
    # ========================================================

    if not os.path.isdir(
        new_db_language_path
    ):

        log(
            f"ERROR: New DB language folder not found."
        )

        failed_languages += 1

        continue


    # ========================================================
    # CHECK DESTINATION ASSETS FOLDER
    # ========================================================

    if not os.path.isdir(
        assets_path
    ):

        log(
            f"ERROR: Assets folder not found."
        )

        failed_languages += 1

        continue


    # ========================================================
    # DELETE EXISTING SQLITE FILES
    # ========================================================

    log(
        "Scanning existing database files..."
    )


    deleted_count = 0


    for file_name in sorted(
        os.listdir(
            assets_path
        )
    ):

        file_path = os.path.join(
            assets_path,
            file_name
        )


        # Only delete SQLite database files
        if (
            os.path.isfile(file_path)
            and file_name.lower().endswith(
                (".sqlite", ".sqlite3", ".db")
            )
        ):

            try:

                os.remove(
                    file_path
                )

                deleted_count += 1
                total_deleted_files += 1

                log(
                    f"DELETED: {file_name}"
                )

            except Exception as e:

                log(
                    f"ERROR deleting {file_name}: {e}"
                )


    log(
        f"Deleted {deleted_count} database files."
    )


    # ========================================================
    # FIND NEW .DB FILES
    # ========================================================

    new_db_files = [
        file_name
        for file_name in sorted(
            os.listdir(
                new_db_language_path
            )
        )
        if (
            os.path.isfile(
                os.path.join(
                    new_db_language_path,
                    file_name
                )
            )
            and file_name.lower().endswith(
                ".db"
            )
        )
    ]


    if not new_db_files:

        log(
            "WARNING: No .db files found in new DB folder."
        )

        failed_languages += 1

        continue


    log(
        f"Found {len(new_db_files)} new .db files."
    )


    # ========================================================
    # COPY NEW DATABASE FILES
    # ========================================================

    copied_count = 0
    copy_failed = False


    for file_name in new_db_files:

        source_file = os.path.join(
            new_db_language_path,
            file_name
        )

        destination_file = os.path.join(
            assets_path,
            file_name
        )


        try:

            shutil.copy2(
                source_file,
                destination_file
            )

            copied_count += 1
            total_copied_files += 1

            log(
                f"COPIED: {file_name}"
            )

        except Exception as e:

            copy_failed = True

            log(
                f"ERROR copying {file_name}: {e}"
            )


    # ========================================================
    # LANGUAGE RESULT
    # ========================================================

    if copy_failed:

        failed_languages += 1

        log(
            f"FAILED: {folder}"
        )

    else:

        successful_languages += 1

        log(
            f"SUCCESS: {folder}"
        )

        log(
            f"Deleted : {deleted_count} files"
        )

        log(
            f"Copied  : {copied_count} files"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

log("")
log("=" * 80)
log("TAFSEER DATABASE REPLACEMENT FINISHED")
log("=" * 80)

log(
    f"Total languages processed : {total_languages}"
)

log(
    f"Successful languages      : {successful_languages}"
)

log(
    f"Failed languages          : {failed_languages}"
)

log(
    f"Total files deleted       : {total_deleted_files}"
)

log(
    f"Total files copied        : {total_copied_files}"
)

log(
    f"Log file                  : {LOG_FILE}"
)

log("=" * 80)