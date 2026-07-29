import os
import json
import sqlite3
import logging
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

# Root containing your language packs
ROOT_DIR = r"H:\CodersInsightWorkSpace\Gwal Apps\Al Quran\HolyQuran-Gwal"

# Folder containing the manually updated mapping JSON
MAPPING_JSON = (
    r"H:\Other Projects\Python\db\tafseer_reports"
    r"\translation_db_mapping.json"
)

# Output folder for comparison reports
OUTPUT_ROOT = r"H:\Other Projects\Python\db\tafseer_reports2"


# ============================================================
# TARGET DATABASE DIRECTORIES
#
# IMPORTANT:
# The order here is the search priority.
#
# 1. Quran.com
# 2. alqurandb.com
# 3. Tartel AI
# ============================================================

TARGET_DATABASE_DIRS = [
    {
        "name": "Quran.com",
        "path": r"E:\QuranSqlAllData\DB Quran.com\databases\translations",
    },
    {
        "name": "alqurandb.com",
        "path": r"E:\QuranSqlAllData\DB alqurandb.com\Translations",
    },
    {
        "name": "Tartel AI",
        "path": r"E:\QuranSqlAllData\DB Tartel Ai\Translations",
    },
]


# ============================================================
# DATABASE FORMATS
# ============================================================

# Your original/source database
SOURCE_TABLE = "ayatafseer"

SOURCE_SURA_COLUMN = "soraid"
SOURCE_AYAH_COLUMN = "ayaid"
SOURCE_TEXT_COLUMN = "tafseer"


# Quran.com
QURAN_COM_TABLE = "verses"

QURAN_COM_SURA_COLUMN = "sura"
QURAN_COM_AYAH_COLUMN = "ayah"
QURAN_COM_TEXT_COLUMN = "text"


# alqurandb.com
# Table name is dynamic and based on the database filename.
#
# Example:
#
# bengali_khan.db
#     table = bengali_khan
#
ALQURANDB_SURA_COLUMN = "sura"
ALQURANDB_AYAH_COLUMN = "aya"
ALQURANDB_TEXT_COLUMN = "text"


# Tartel AI
TARTEL_TABLE = "translation"

TARTEL_SURA_COLUMN = "sura"
TARTEL_AYAH_COLUMN = "ayah"
TARTEL_TEXT_COLUMN = "text"


# Supported SQLite extensions
SUPPORTED_DB_EXTENSIONS = (
    ".db",
    ".sqlite",
    ".sqlite3",
)


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

os.makedirs(OUTPUT_ROOT, exist_ok=True)

REPORTS_DIR = os.path.join(
    OUTPUT_ROOT,
    "reports"
)

os.makedirs(REPORTS_DIR, exist_ok=True)


# ============================================================
# LOGGING
# ============================================================

LOG_FILE = os.path.join(
    OUTPUT_ROOT,
    "comparison.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            mode="w",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_db_name(name):
    """
    Normalize a database name for comparison.

    Examples:

        quran.al
        quran.al.db
        quran.al.sqlite

    All are normalized to:

        quran.al
    """

    if name is None:
        return None

    name = str(name).strip()

    if not name:
        return None

    lower_name = name.lower()

    for extension in SUPPORTED_DB_EXTENSIONS:
        if lower_name.endswith(extension):
            name = name[:-len(extension)]
            break

    return name.lower()


def get_file_without_extension(file_name):
    """
    Return filename without .db/.sqlite/.sqlite3.
    """

    base_name = os.path.basename(file_name)

    for extension in SUPPORTED_DB_EXTENSIONS:
        if base_name.lower().endswith(extension):
            return base_name[:-len(extension)]

    return os.path.splitext(base_name)[0]


def find_target_database(target_name):
    """
    Search for the target database in priority order.

    Priority:

    1. Quran.com
    2. alqurandb.com
    3. Tartel AI

    Returns:

    {
        "provider": "...",
        "path": "...",
        "file_name": "..."
    }

    or None if not found.
    """

    normalized_target = normalize_db_name(target_name)

    if normalized_target is None:
        return None

    logger.info(
        "Searching target database: %s",
        target_name
    )

    for source in TARGET_DATABASE_DIRS:

        provider_name = source["name"]
        directory = source["path"]

        if not os.path.isdir(directory):

            logger.warning(
                "Directory does not exist: [%s] %s",
                provider_name,
                directory
            )

            continue

        try:
            files = os.listdir(directory)

        except Exception as e:

            logger.warning(
                "Cannot read directory [%s]: %s",
                provider_name,
                e
            )

            continue

        for file_name in files:

            if not file_name.lower().endswith(
                SUPPORTED_DB_EXTENSIONS
            ):
                continue

            file_without_extension = (
                get_file_without_extension(file_name)
            )

            normalized_file = normalize_db_name(
                file_without_extension
            )

            if normalized_file == normalized_target:

                full_path = os.path.join(
                    directory,
                    file_name
                )

                logger.info(
                    "FOUND target database: %s | Provider: %s",
                    file_name,
                    provider_name
                )

                return {
                    "provider": provider_name,
                    "path": full_path,
                    "file_name": file_name,
                }

    logger.warning(
        "Target database NOT FOUND: %s",
        target_name
    )

    return None


def find_source_database(
    translation_id,
    language_pack
):
    """
    Find source database.

    Expected filename:

        tafseer<ID>.sqlite

    Example:

        Translation ID 202
        -> tafseer202.sqlite
    """

    assets_path = os.path.join(
        ROOT_DIR,
        language_pack,
        "src",
        "main",
        "assets"
    )

    if not os.path.isdir(assets_path):

        logger.warning(
            "Assets directory not found: %s",
            assets_path
        )

        return None

    expected_base_name = (
        f"tafseer{translation_id}"
    ).lower()

    candidates = []

    try:
        files = os.listdir(assets_path)

    except Exception as e:

        logger.error(
            "Cannot read assets directory %s: %s",
            assets_path,
            e
        )

        return None

    for file_name in files:

        if not file_name.lower().endswith(
            SUPPORTED_DB_EXTENSIONS
        ):
            continue

        file_without_extension = (
            get_file_without_extension(file_name)
        ).lower()

        if file_without_extension == expected_base_name:

            candidates.append(
                os.path.join(
                    assets_path,
                    file_name
                )
            )

    if not candidates:

        logger.warning(
            "Source database not found for Translation ID %s. "
            "Expected: %s.[db|sqlite|sqlite3]",
            translation_id,
            expected_base_name
        )

        return None

    if len(candidates) > 1:

        logger.warning(
            "Multiple source databases found for Translation ID %s. "
            "Using first: %s",
            translation_id,
            candidates[0]
        )

    return candidates[0]


def get_table_names(conn):
    """
    Return all SQLite table names.
    """

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    return [
        row[0]
        for row in cursor.fetchall()
    ]


def table_exists(
    conn,
    table_name
):
    """
    Check if a table exists.
    """

    tables = get_table_names(conn)

    return table_name in tables


def get_table_columns(
    conn,
    table_name
):
    """
    Return column names for a table.
    """

    cursor = conn.cursor()

    cursor.execute(
        f'PRAGMA table_info("{table_name}")'
    )

    return [
        row[1]
        for row in cursor.fetchall()
    ]


def validate_columns(
    conn,
    table_name,
    required_columns
):
    """
    Validate that required columns exist.
    """

    if not table_exists(
        conn,
        table_name
    ):
        return False, (
            f"Table '{table_name}' does not exist. "
            f"Available tables: {get_table_names(conn)}"
        )

    columns = get_table_columns(
        conn,
        table_name
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in columns
    ]

    if missing_columns:

        return False, (
            f"Missing columns {missing_columns} "
            f"in table '{table_name}'. "
            f"Available columns: {columns}"
        )

    return True, None


def get_source_table_config():
    """
    Return source DB table configuration.
    """

    return {
        "table": SOURCE_TABLE,
        "sura_column": SOURCE_SURA_COLUMN,
        "ayah_column": SOURCE_AYAH_COLUMN,
        "text_column": SOURCE_TEXT_COLUMN,
    }


def get_target_table_config(
    provider,
    db_path
):
    """
    Return target DB configuration based on provider.

    Quran.com:
        table = verses

    alqurandb.com:
        table = database filename without extension

    Tartel AI:
        table = translation
    """

    if provider == "Quran.com":

        return {
            "table": QURAN_COM_TABLE,
            "sura_column": QURAN_COM_SURA_COLUMN,
            "ayah_column": QURAN_COM_AYAH_COLUMN,
            "text_column": QURAN_COM_TEXT_COLUMN,
        }

    if provider == "alqurandb.com":

        file_name = os.path.basename(
            db_path
        )

        table_name = get_file_without_extension(
            file_name
        )

        return {
            "table": table_name,
            "sura_column": ALQURANDB_SURA_COLUMN,
            "ayah_column": ALQURANDB_AYAH_COLUMN,
            "text_column": ALQURANDB_TEXT_COLUMN,
        }

    if provider == "Tartel AI":

        return {
            "table": TARTEL_TABLE,
            "sura_column": TARTEL_SURA_COLUMN,
            "ayah_column": TARTEL_AYAH_COLUMN,
            "text_column": TARTEL_TEXT_COLUMN,
        }

    raise ValueError(
        f"Unknown provider: {provider}"
    )


def load_source_rows(
    db_path
):
    """
    Load source translation data.

    Returns dictionary:

        {
            (sura, ayah): text
        }
    """

    config = get_source_table_config()

    conn = None

    try:

        conn = sqlite3.connect(
            db_path
        )

        valid, error = validate_columns(
            conn,
            config["table"],
            [
                config["sura_column"],
                config["ayah_column"],
                config["text_column"],
            ]
        )

        if not valid:

            raise RuntimeError(
                error
            )

        cursor = conn.cursor()

        query = f'''
            SELECT
                "{config["sura_column"]}",
                "{config["ayah_column"]}",
                "{config["text_column"]}"
            FROM "{config["table"]}"
        '''

        cursor.execute(query)

        rows = {}

        duplicate_count = 0

        for sura, ayah, text in cursor.fetchall():

            key = (
                int(sura),
                int(ayah)
            )

            if key in rows:
                duplicate_count += 1

            rows[key] = (
                "" if text is None
                else str(text)
            )

        if duplicate_count > 0:

            logger.warning(
                "Source DB has %s duplicate verse keys: %s",
                duplicate_count,
                db_path
            )

        return rows

    finally:

        if conn is not None:
            conn.close()


def load_target_rows(
    db_path,
    provider
):
    """
    Load target translation data.

    Returns dictionary:

        {
            (sura, ayah): text
        }
    """

    config = get_target_table_config(
        provider,
        db_path
    )

    conn = None

    try:

        conn = sqlite3.connect(
            db_path
        )

        valid, error = validate_columns(
            conn,
            config["table"],
            [
                config["sura_column"],
                config["ayah_column"],
                config["text_column"],
            ]
        )

        if not valid:

            raise RuntimeError(
                error
            )

        cursor = conn.cursor()

        query = f'''
            SELECT
                "{config["sura_column"]}",
                "{config["ayah_column"]}",
                "{config["text_column"]}"
            FROM "{config["table"]}"
        '''

        cursor.execute(query)

        rows = {}

        duplicate_count = 0

        for sura, ayah, text in cursor.fetchall():

            key = (
                int(sura),
                int(ayah)
            )

            if key in rows:
                duplicate_count += 1

            rows[key] = (
                "" if text is None
                else str(text)
            )

        if duplicate_count > 0:

            logger.warning(
                "Target DB has %s duplicate verse keys: %s",
                duplicate_count,
                db_path
            )

        return rows

    finally:

        if conn is not None:
            conn.close()


def compare_translation(
    source_rows,
    target_rows
):
    """
    Compare two translation dictionaries.

    Comparison key:

        (sura, ayah)

    Text comparison:

        Exact character-by-character comparison.
    """

    differences = []

    missing_in_target = []

    missing_in_source = []

    matched = 0

    source_keys = set(
        source_rows.keys()
    )

    target_keys = set(
        target_rows.keys()
    )

    common_keys = (
        source_keys &
        target_keys
    )

    for key in sorted(
        common_keys
    ):

        source_text = source_rows[key]
        target_text = target_rows[key]

        if source_text == target_text:

            matched += 1

        else:

            sura, ayah = key

            differences.append(
                {
                    "sura": sura,
                    "ayah": ayah,
                    "source_text": source_text,
                    "comparison_text": target_text,
                }
            )

    for key in sorted(
        source_keys - target_keys
    ):

        sura, ayah = key

        missing_in_target.append(
            {
                "sura": sura,
                "ayah": ayah,
                "source_text": source_rows[key],
            }
        )

    for key in sorted(
        target_keys - source_keys
    ):

        sura, ayah = key

        missing_in_source.append(
            {
                "sura": sura,
                "ayah": ayah,
                "comparison_text": target_rows[key],
            }
        )

    return {
        "matched": matched,
        "different": len(
            differences
        ),
        "missing_in_target": len(
            missing_in_target
        ),
        "missing_in_source": len(
            missing_in_source
        ),
        "differences": differences,
        "missing_in_target_rows": missing_in_target,
        "missing_in_source_rows": missing_in_source,
    }


def safe_folder_name(
    translation_id,
    language,
    translator
):
    """
    Create a safe folder name for Windows.
    """

    name_parts = [
        str(translation_id),
        language
    ]

    if translator:
        name_parts.append(
            translator
        )

    name = "_".join(
        name_parts
    )

    invalid_chars = (
        '<>:"/\\|?*'
    )

    for char in invalid_chars:

        name = name.replace(
            char,
            "_"
        )

    name = name.replace(
        "\n",
        " "
    )

    name = name.replace(
        "\r",
        " "
    )

    return name.strip()


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = datetime.now()

    logger.info(
        "=" * 80
    )

    logger.info(
        "TAFSEER TRANSLATION DATABASE COMPARISON STARTED"
    )

    logger.info(
        "Started at: %s",
        start_time
    )

    logger.info(
        "Mapping JSON: %s",
        MAPPING_JSON
    )

    logger.info(
        "Output directory: %s",
        OUTPUT_ROOT
    )

    logger.info(
        "=" * 80
    )


    # --------------------------------------------------------
    # CHECK MAPPING JSON
    # --------------------------------------------------------

    if not os.path.isfile(
        MAPPING_JSON
    ):

        logger.error(
            "Mapping JSON not found: %s",
            MAPPING_JSON
        )

        return


    # --------------------------------------------------------
    # LOAD MAPPING
    # --------------------------------------------------------

    try:

        with open(
            MAPPING_JSON,
            "r",
            encoding="utf-8"
        ) as f:

            mappings = json.load(f)

    except Exception as e:

        logger.error(
            "Failed to read mapping JSON: %s",
            e
        )

        return


    if not isinstance(
        mappings,
        list
    ):

        logger.error(
            "Mapping JSON must contain a JSON array."
        )

        return


    # --------------------------------------------------------
    # SUMMARY COUNTERS
    # --------------------------------------------------------

    total_translations = len(
        mappings
    )

    skipped_null_target = 0

    skipped_missing_source = 0

    target_not_found = 0

    successfully_compared = 0

    failed_comparisons = 0

    total_matched = 0

    total_different = 0

    total_missing_target = 0

    total_missing_source = 0


    combined_results = []


    # ========================================================
    # PROCESS EACH TRANSLATION
    # ========================================================

    for index, item in enumerate(
        mappings,
        start=1
    ):

        translation_id = item.get(
            "id"
        )

        language = item.get(
            "language",
            ""
        )

        translator = item.get(
            "translator",
            ""
        )

        language_pack = item.get(
            "language_pack",
            ""
        )

        target_db_name = item.get(
            "quran_com_db"
        )


        logger.info(
            ""
        )

        logger.info(
            "=" * 80
        )

        logger.info(
            "[%s/%s] Processing Translation ID: %s",
            index,
            total_translations,
            translation_id
        )

        logger.info(
            "Language: %s",
            language
        )

        logger.info(
            "Translator: %s",
            translator
        )

        logger.info(
            "Language Pack: %s",
            language_pack
        )


        # ----------------------------------------------------
        # CHECK NULL TARGET
        # ----------------------------------------------------

        if (
            target_db_name is None
            or str(
                target_db_name
            ).strip() == ""
        ):

            logger.info(
                "SKIPPED: quran_com_db is NULL."
            )

            skipped_null_target += 1

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "SKIPPED_NULL_TARGET",
                    "quran_com_db": None,
                }
            )

            continue


        # ----------------------------------------------------
        # FIND SOURCE DATABASE
        # ----------------------------------------------------

        source_db_path = find_source_database(
            translation_id,
            language_pack
        )

        if source_db_path is None:

            skipped_missing_source += 1

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "SOURCE_DB_NOT_FOUND",
                    "quran_com_db": target_db_name,
                }
            )

            continue


        logger.info(
            "Source DB: %s",
            source_db_path
        )


        # ----------------------------------------------------
        # FIND TARGET DATABASE
        # ----------------------------------------------------

        target_info = find_target_database(
            target_db_name
        )

        if target_info is None:

            target_not_found += 1

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "TARGET_DB_NOT_FOUND",
                    "source_db": os.path.basename(
                        source_db_path
                    ),
                    "quran_com_db": target_db_name,
                    "comparison_provider": None,
                }
            )

            continue


        target_db_path = target_info[
            "path"
        ]

        provider = target_info[
            "provider"
        ]

        target_file_name = target_info[
            "file_name"
        ]


        logger.info(
            "Target DB: %s",
            target_file_name
        )

        logger.info(
            "Provider: %s",
            provider
        )


        # ----------------------------------------------------
        # LOAD SOURCE
        # ----------------------------------------------------

        try:

            source_rows = load_source_rows(
                source_db_path
            )

            logger.info(
                "Source rows loaded: %s",
                len(source_rows)
            )

        except Exception as e:

            failed_comparisons += 1

            logger.exception(
                "Failed to load source DB: %s",
                e
            )

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "SOURCE_DB_ERROR",
                    "source_db": os.path.basename(
                        source_db_path
                    ),
                    "quran_com_db": target_db_name,
                    "comparison_provider": provider,
                    "error": str(e),
                }
            )

            continue


        # ----------------------------------------------------
        # LOAD TARGET
        # ----------------------------------------------------

        try:

            target_rows = load_target_rows(
                target_db_path,
                provider
            )

            logger.info(
                "Target rows loaded: %s",
                len(target_rows)
            )

        except Exception as e:

            failed_comparisons += 1

            logger.exception(
                "Failed to load target DB: %s",
                e
            )

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "TARGET_DB_ERROR",
                    "source_db": os.path.basename(
                        source_db_path
                    ),
                    "quran_com_db": target_db_name,
                    "comparison_provider": provider,
                    "target_db": target_file_name,
                    "error": str(e),
                }
            )

            continue


        # ----------------------------------------------------
        # COMPARE
        # ----------------------------------------------------

        try:

            comparison = compare_translation(
                source_rows,
                target_rows
            )

        except Exception as e:

            failed_comparisons += 1

            logger.exception(
                "Comparison failed: %s",
                e
            )

            combined_results.append(
                {
                    "id": translation_id,
                    "language": language,
                    "translator": translator,
                    "language_pack": language_pack,
                    "status": "COMPARISON_ERROR",
                    "source_db": os.path.basename(
                        source_db_path
                    ),
                    "quran_com_db": target_db_name,
                    "comparison_provider": provider,
                    "target_db": target_file_name,
                    "error": str(e),
                }
            )

            continue


        successfully_compared += 1

        total_matched += comparison[
            "matched"
        ]

        total_different += comparison[
            "different"
        ]

        total_missing_target += comparison[
            "missing_in_target"
        ]

        total_missing_source += comparison[
            "missing_in_source"
        ]


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if (
            comparison["different"] == 0
            and comparison[
                "missing_in_target"
            ] == 0
            and comparison[
                "missing_in_source"
            ] == 0
        ):

            status = "MATCH"

            logger.info(
                "RESULT: MATCH"
            )

        else:

            status = "DIFFERENCES_FOUND"

            logger.warning(
                "RESULT: DIFFERENCES FOUND"
            )


        logger.info(
            "Matched: %s",
            comparison[
                "matched"
            ]
        )

        logger.info(
            "Different: %s",
            comparison[
                "different"
            ]
        )

        logger.info(
            "Missing in target: %s",
            comparison[
                "missing_in_target"
            ]
        )

        logger.info(
            "Missing in source: %s",
            comparison[
                "missing_in_source"
            ]
        )


        # ----------------------------------------------------
        # INDIVIDUAL REPORT
        # ----------------------------------------------------

        report = {
            "translation_id": translation_id,
            "language": language,
            "translator": translator,
            "language_pack": language_pack,

            "source_db": os.path.basename(
                source_db_path
            ),

            "source_db_path": source_db_path,

            "comparison_db": target_file_name,

            "comparison_db_path": target_db_path,

            "comparison_provider": provider,

            "status": status,

            "total_source_rows": len(
                source_rows
            ),

            "total_comparison_rows": len(
                target_rows
            ),

            "matched_rows": comparison[
                "matched"
            ],

            "different_rows": comparison[
                "different"
            ],

            "missing_in_target": comparison[
                "missing_in_target"
            ],

            "missing_in_source": comparison[
                "missing_in_source"
            ],

            "differences": comparison[
                "differences"
            ],

            "missing_in_target_rows": comparison[
                "missing_in_target_rows"
            ],

            "missing_in_source_rows": comparison[
                "missing_in_source_rows"
            ],
        }


        # ----------------------------------------------------
        # CREATE REPORT DIRECTORY
        # ----------------------------------------------------

        report_folder_name = safe_folder_name(
            translation_id,
            language,
            translator
        )

        report_folder = os.path.join(
            REPORTS_DIR,
            report_folder_name
        )

        os.makedirs(
            report_folder,
            exist_ok=True
        )


        # ----------------------------------------------------
        # WRITE INDIVIDUAL JSON
        # ----------------------------------------------------

        report_json_path = os.path.join(
            report_folder,
            "comparison.json"
        )

        with open(
            report_json_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                report,
                f,
                ensure_ascii=False,
                indent=2
            )


        # ----------------------------------------------------
        # ADD TO COMBINED RESULTS
        # ----------------------------------------------------

        combined_results.append(
            report
        )


    # ========================================================
    # WRITE COMBINED JSON
    # ========================================================

    combined_json_path = os.path.join(
        OUTPUT_ROOT,
        "combined_comparison.json"
    )

    combined_summary = {
        "generated_at": datetime.now().isoformat(),

        "configuration": {
            "root_dir": ROOT_DIR,
            "mapping_json": MAPPING_JSON,
            "target_database_directories": TARGET_DATABASE_DIRS,
        },

        "summary": {
            "total_translations": total_translations,
            "successfully_compared": successfully_compared,
            "skipped_null_target": skipped_null_target,
            "skipped_missing_source": skipped_missing_source,
            "target_not_found": target_not_found,
            "failed_comparisons": failed_comparisons,
            "total_matched_rows": total_matched,
            "total_different_rows": total_different,
            "total_missing_in_target": total_missing_target,
            "total_missing_in_source": total_missing_source,
        },

        "translations": combined_results,
    }


    with open(
        combined_json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            combined_summary,
            f,
            ensure_ascii=False,
            indent=2
        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    end_time = datetime.now()

    duration = (
        end_time -
        start_time
    )

    logger.info(
        ""
    )

    logger.info(
        "=" * 80
    )

    logger.info(
        "COMPARISON FINISHED"
    )

    logger.info(
        "=" * 80
    )

    logger.info(
        "Total translations       : %s",
        total_translations
    )

    logger.info(
        "Successfully compared    : %s",
        successfully_compared
    )

    logger.info(
        "Skipped NULL target      : %s",
        skipped_null_target
    )

    logger.info(
        "Missing source DB        : %s",
        skipped_missing_source
    )

    logger.info(
        "Target DB not found      : %s",
        target_not_found
    )

    logger.info(
        "Failed comparisons       : %s",
        failed_comparisons
    )

    logger.info(
        "Total matched rows       : %s",
        total_matched
    )

    logger.info(
        "Total different rows     : %s",
        total_different
    )

    logger.info(
        "Missing in target        : %s",
        total_missing_target
    )

    logger.info(
        "Missing in source        : %s",
        total_missing_source
    )

    logger.info(
        "Combined JSON            : %s",
        combined_json_path
    )

    logger.info(
        "Reports directory        : %s",
        REPORTS_DIR
    )

    logger.info(
        "Log file                 : %s",
        LOG_FILE
    )

    logger.info(
        "Duration                 : %s",
        duration
    )

    logger.info(
        "=" * 80
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()