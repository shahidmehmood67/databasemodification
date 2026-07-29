import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List


# ============================================================
# CONFIGURATION
# ============================================================

# Folder containing the manually updated mapping JSON
MAPPING_JSON = (
    r"H:\Other Projects\Python\db\tafseer_reports"
    r"\translation_db_mapping.json"
)

# Output folder for newly created standardized databases
OUTPUT_ROOT = r"H:\Other Projects\Python\db\tafseer_newdb"


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
        "path": r"E:\QuranSqlAllData\DB New Translations\selected\Quran.com",
    },
    {
        "name": "alqurandb.com",
        "path": r"E:\QuranSqlAllData\DB New Translations\selected\alqurandb.com",
    },
    {
        "name": "Tartel AI",
        "path": r"E:\QuranSqlAllData\DB New Translations\selected\tarteel ai",
    },
]


# ============================================================
# DATABASE FORMATS
# ============================================================

# ------------------------------------------------------------
# Quran.com
# ------------------------------------------------------------

QURAN_COM_TABLE = "verses"

QURAN_COM_SURA_COLUMN = "sura"
QURAN_COM_AYAH_COLUMN = "ayah"
QURAN_COM_TEXT_COLUMN = "text"


# ------------------------------------------------------------
# alqurandb.com
#
# Table name is dynamic and based on database filename.
#
# Example:
#
# bengali_khan.db
#     table = bengali_khan
# ------------------------------------------------------------

ALQURANDB_SURA_COLUMN = "sura"
ALQURANDB_AYAH_COLUMN = "aya"
ALQURANDB_TEXT_COLUMN = "text"


# ------------------------------------------------------------
# Tartel AI
# ------------------------------------------------------------

TARTEL_TABLE = "translation"

TARTEL_SURA_COLUMN = "sura"
TARTEL_AYAH_COLUMN = "ayah"
TARTEL_TEXT_COLUMN = "text"


# ============================================================
# NEW STANDARD DATABASE FORMAT
#
# Every newly created database will use this structure.
# ============================================================

OUTPUT_TABLE = "verses"

OUTPUT_SURA_COLUMN = "sura"
OUTPUT_AYAH_COLUMN = "ayah"
OUTPUT_TEXT_COLUMN = "text"


# ============================================================
# OPTIONS
# ============================================================

# If True, an existing output database will be deleted
# and recreated.
#
# If False, an existing complete database will be skipped.
OVERWRITE_EXISTING = False


# If True, source databases are searched recursively
# inside their configured directories.
RECURSIVE_SEARCH = True


# ============================================================
# LOGGING
# ============================================================

LOG_FILE = Path(OUTPUT_ROOT) / "create_translation_databases.log"

Path(OUTPUT_ROOT).mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# STATISTICS
# ============================================================

stats = {
    "total_mappings": 0,
    "processed": 0,
    "created": 0,
    "skipped": 0,
    "source_not_found": 0,
    "failed": 0,
    "empty_source": 0,
    "total_rows_created": 0,

    "source_quran_com": 0,
    "source_alqurandb": 0,
    "source_tartel": 0,
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_name(value: str) -> str:
    """
    Convert a language/translator name into a safe filename.

    Example:
        Sahih International
        ->
        sahih_international
    """

    value = str(value).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value
    )

    value = re.sub(
        r"_+",
        "_",
        value
    )

    return value.strip("_")


def get_output_database_name(
    language: str,
    translator: str
) -> str:
    """
    Create output DB filename.

    Example:
        English
        Sahih International

        ->
        english_sahih_international.db
    """

    language_name = normalize_name(language)
    translator_name = normalize_name(translator)

    if translator_name:
        return f"{language_name}_{translator_name}.db"

    return f"{language_name}.db"


def get_database_stem(path: Path) -> str:
    """
    Get database filename without extension.

    Example:
        quran.ensi.sqlite
        ->
        quran.ensi
    """

    return path.stem


def find_source_databaseold(
    quran_com_db: str
) -> Optional[Dict]:

    """
    Search for source database.

    Search priority:

    1. Quran.com
    2. alqurandb.com
    3. Tartel AI

    The extension is ignored.

    Example:

        quran.ensi

    can match:

        quran.ensi.db
        quran.ensi.sqlite
        quran.ensi.sqlite3
    """

    requested_name = Path(
        quran_com_db
    ).stem.lower()

    logger.info(
        "Searching source database: %s",
        requested_name
    )

    for target in TARGET_DATABASE_DIRS:

        source_name = target["name"]
        source_root = Path(
            target["path"]
        )

        if not source_root.exists():

            logger.warning(
                "Source directory does not exist: %s | %s",
                source_name,
                source_root
            )

            continue

        if RECURSIVE_SEARCH:
            database_files = [
                file
                for file in source_root.rglob("*")
                if file.is_file()
            ]
        else:
            database_files = [
                file
                for file in source_root.iterdir()
                if file.is_file()
            ]

        for file in database_files:

            # Ignore non-database files
            if file.suffix.lower() not in (
                ".db",
                ".sqlite",
                ".sqlite3"
            ):
                continue

            file_stem = get_database_stem(
                file
            ).lower()

            if file_stem == requested_name:

                logger.info(
                    "Source database found | Source: %s | Path: %s",
                    source_name,
                    file
                )

                return {
                    "name": source_name,
                    "path": file
                }

    logger.warning(
        "Source database NOT FOUND: %s",
        quran_com_db
    )

    return None

def find_source_database(
    quran_com_db: str
) -> Optional[Dict]:

    """
    Search for source database.

    Search priority:

    1. Quran.com
    2. alqurandb.com
    3. Tartel AI

    The extension is ignored.

    Example:

        quran.al

    can match:

        quran.al.db
        quran.al.sqlite
        quran.al.sqlite3
    """

    requested_name = normalize_database_name(
        quran_com_db
    )

    logger.info(
        "============================================================"
    )

    logger.info(
        "SOURCE DATABASE SEARCH STARTED"
    )

    logger.info(
        "Requested DB identifier: %s",
        quran_com_db
    )

    logger.info(
        "Normalized DB name: %s",
        requested_name
    )

    logger.info(
        "Search priority: Quran.com -> alqurandb.com -> Tartel AI"
    )

    for target in TARGET_DATABASE_DIRS:

        source_name = target["name"]
        source_root = Path(
            target["path"]
        )

        logger.info(
            ""
        )

        logger.info(
            "Checking source: %s",
            source_name
        )

        logger.info(
            "Directory: %s",
            source_root
        )

        # ----------------------------------------------------
        # Check directory
        # ----------------------------------------------------

        if not source_root.exists():

            logger.error(
                "DIRECTORY DOES NOT EXIST: %s",
                source_root
            )

            continue

        if not source_root.is_dir():

            logger.error(
                "PATH IS NOT A DIRECTORY: %s",
                source_root
            )

            continue

        logger.info(
            "Directory exists: YES"
        )

        # ----------------------------------------------------
        # Find files
        # ----------------------------------------------------

        if RECURSIVE_SEARCH:

            logger.info(
                "Search mode: RECURSIVE"
            )

            all_files = list(
                source_root.rglob("*")
            )

        else:

            logger.info(
                "Search mode: CURRENT DIRECTORY ONLY"
            )

            all_files = list(
                source_root.iterdir()
            )

        files = [
            file
            for file in all_files
            if file.is_file()
        ]

        logger.info(
            "Total files found: %s",
            len(files)
        )

        # ----------------------------------------------------
        # Database files
        # ----------------------------------------------------

        database_files = [
            file
            for file in files
            if file.suffix.lower() in (
                ".db",
                ".sqlite",
                ".sqlite3"
            )
        ]

        logger.info(
            "Database files found: %s",
            len(database_files)
        )

        # ----------------------------------------------------
        # Debug: show all database files
        # ----------------------------------------------------

        if database_files:

            logger.info(
                "Available database files:"
            )

            for file in database_files:

                logger.info(
                    "    - Filename: %s | Stem: %s | Full Path: %s",
                    file.name,
                    file.stem,
                    file
                )

        else:

            logger.warning(
                "NO DATABASE FILES FOUND in: %s",
                source_root
            )

        # ----------------------------------------------------
        # Try matching
        # ----------------------------------------------------

        logger.info(
            "Looking for database name: %s",
            requested_name
        )

        for file in database_files:

            file_stem = normalize_database_name(
                file.name
            )

            logger.debug(
                "Comparing requested='%s' with file_stem='%s'",
                requested_name,
                file_stem
            )

            if file_stem == requested_name:

                logger.info(
                    "============================================================"
                )

                logger.info(
                    "SOURCE DATABASE MATCH FOUND"
                )

                logger.info(
                    "Source: %s",
                    source_name
                )

                logger.info(
                    "Requested: %s",
                    quran_com_db
                )

                logger.info(
                    "Matched filename: %s",
                    file.name
                )

                logger.info(
                    "Matched stem: %s",
                    file.stem
                )

                logger.info(
                    "Full path: %s",
                    file
                )

                logger.info(
                    "============================================================"
                )

                return {
                    "name": source_name,
                    "path": file
                }

        logger.info(
            "No match found in %s",
            source_name
        )

    # --------------------------------------------------------
    # Nothing found
    # --------------------------------------------------------

    logger.error(
        "============================================================"
    )

    logger.error(
        "SOURCE DATABASE NOT FOUND"
    )

    logger.error(
        "Requested DB: %s",
        quran_com_db
    )

    logger.error(
        "Normalized name: %s",
        requested_name
    )

    logger.error(
        "Searched all configured source directories."
    )

    logger.error(
        "============================================================"
    )

    return None


def get_table_names(
    connection: sqlite3.Connection
) -> List[str]:

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    )

    return [
        row[0]
        for row in cursor.fetchall()
    ]

def normalize_database_name(
    database_name: str
) -> str:

    name = str(
        database_name
    ).strip().lower()

    for extension in (
        ".db",
        ".sqlite",
        ".sqlite3"
    ):
        if name.endswith(extension):
            name = name[
                :-len(extension)
            ]
            break

    return name


def get_source_table(
    source_name: str,
    source_path: Path,
    connection: sqlite3.Connection
) -> Optional[str]:

    tables = get_table_names(
        connection
    )

    if source_name == "Quran.com":

        if QURAN_COM_TABLE in tables:
            return QURAN_COM_TABLE

        logger.error(
            "Quran.com table '%s' not found in %s",
            QURAN_COM_TABLE,
            source_path
        )

        return None

    if source_name == "Tartel AI":

        if TARTEL_TABLE in tables:
            return TARTEL_TABLE

        logger.error(
            "Tartel AI table '%s' not found in %s",
            TARTEL_TABLE,
            source_path
        )

        return None

    if source_name == "alqurandb.com":

        expected_table = source_path.stem

        if expected_table in tables:
            return expected_table

        # Case-insensitive fallback
        for table in tables:

            if table.lower() == expected_table.lower():
                return table

        logger.error(
            "alqurandb.com dynamic table '%s' not found in %s",
            expected_table,
            source_path
        )

        return None

    logger.error(
        "Unknown source: %s",
        source_name
    )

    return None


def get_source_columns(
    source_name: str
):
    """
    Return the source-specific column names.
    """

    if source_name == "Quran.com":

        return (
            QURAN_COM_SURA_COLUMN,
            QURAN_COM_AYAH_COLUMN,
            QURAN_COM_TEXT_COLUMN
        )

    if source_name == "alqurandb.com":

        return (
            ALQURANDB_SURA_COLUMN,
            ALQURANDB_AYAH_COLUMN,
            ALQURANDB_TEXT_COLUMN
        )

    if source_name == "Tartel AI":

        return (
            TARTEL_SURA_COLUMN,
            TARTEL_AYAH_COLUMN,
            TARTEL_TEXT_COLUMN
        )

    raise ValueError(
        f"Unknown source: {source_name}"
    )


def create_output_database(
    output_path: Path
):
    """
    Create a new standardized database.
    """

    if output_path.exists():

        if OVERWRITE_EXISTING:

            logger.warning(
                "Output already exists. Removing: %s",
                output_path
            )

            output_path.unlink()

        else:

            logger.info(
                "Output database already exists. Skipping creation: %s",
                output_path
            )

            return False

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        output_path
    )

    try:

        cursor = connection.cursor()

        cursor.execute(
            f"""
            CREATE TABLE {OUTPUT_TABLE} (
                {OUTPUT_SURA_COLUMN} INTEGER NOT NULL,
                {OUTPUT_AYAH_COLUMN} INTEGER NOT NULL,
                {OUTPUT_TEXT_COLUMN} TEXT
            )
            """
        )

        cursor.execute(
            f"""
            CREATE INDEX idx_{OUTPUT_TABLE}_sura_ayah
            ON {OUTPUT_TABLE} (
                {OUTPUT_SURA_COLUMN},
                {OUTPUT_AYAH_COLUMN}
            )
            """
        )

        connection.commit()

    finally:

        connection.close()

    return True


def output_database_is_complete(
    output_path: Path
) -> bool:

    """
    Check whether an existing output database
    has the expected verses table and records.
    """

    if not output_path.exists():
        return False

    try:

        connection = sqlite3.connect(
            output_path
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
            """,
            (
                OUTPUT_TABLE,
            )
        )

        table_exists = (
            cursor.fetchone()
            is not None
        )

        if not table_exists:

            connection.close()

            return False

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {OUTPUT_TABLE}
            """
        )

        count = cursor.fetchone()[0]

        connection.close()

        return count > 0

    except Exception:

        return False


def read_source_rows(
    source_name: str,
    source_path: Path
):

    """
    Read all translation rows from source database.
    """

    connection = sqlite3.connect(
        source_path
    )

    try:

        table = get_source_table(
            source_name,
            source_path,
            connection
        )

        if table is None:

            return []

        (
            sura_column,
            ayah_column,
            text_column
        ) = get_source_columns(
            source_name
        )

        logger.info(
            "Reading source | Table: %s | Columns: %s, %s, %s",
            table,
            sura_column,
            ayah_column,
            text_column
        )

        cursor = connection.cursor()

        query = f"""
            SELECT
                "{sura_column}",
                "{ayah_column}",
                "{text_column}"
            FROM "{table}"
        """

        cursor.execute(
            query
        )

        rows = cursor.fetchall()

        return rows

    finally:

        connection.close()


def insert_rows(
    output_path: Path,
    rows
) -> Dict:

    """
    Insert source rows into standardized output DB.
    """

    connection = sqlite3.connect(
        output_path
    )

    inserted = 0
    skipped = 0

    try:

        cursor = connection.cursor()

        for row in rows:

            if len(row) < 3:

                skipped += 1

                continue

            sura = row[0]
            ayah = row[1]
            text = row[2]

            if sura is None or ayah is None:

                skipped += 1

                continue

            cursor.execute(
                f"""
                INSERT INTO {OUTPUT_TABLE}
                (
                    {OUTPUT_SURA_COLUMN},
                    {OUTPUT_AYAH_COLUMN},
                    {OUTPUT_TEXT_COLUMN}
                )
                VALUES (?, ?, ?)
                """,
                (
                    sura,
                    ayah,
                    text
                )
            )

            inserted += 1

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

    return {
        "inserted": inserted,
        "skipped": skipped
    }


# ============================================================
# PROCESS ONE MAPPING
# ============================================================

def process_mapping(
    mapping: Dict,
    index: int,
    total: int
):

    language = str(
        mapping.get(
            "language",
            ""
        )
    ).strip()

    translator = str(
        mapping.get(
            "translator",
            ""
        )
    ).strip()

    language_pack = str(
        mapping.get(
            "language_pack",
            ""
        )
    ).strip()

    quran_com_db = str(
        mapping.get(
            "quran_com_db",
            ""
        )
    ).strip()

    logger.info(
        ""
    )

    logger.info(
        "============================================================"
    )

    logger.info(
        "PROCESSING %s/%s",
        index,
        total
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

    logger.info(
        "Source DB Identifier: %s",
        quran_com_db
    )

    # Validate required fields
    if not language:

        logger.error(
            "Missing language"
        )

        stats["failed"] += 1

        return

    if not translator:

        logger.error(
            "Missing translator"
        )

        stats["failed"] += 1

        return

    if not language_pack:

        logger.error(
            "Missing language_pack"
        )

        stats["failed"] += 1

        return

    if not quran_com_db:

        logger.error(
            "Missing quran_com_db"
        )

        stats["failed"] += 1

        return

    # --------------------------------------------------------
    # Find source database
    # --------------------------------------------------------

    source = find_source_database(
        quran_com_db
    )

    if source is None:

        stats["source_not_found"] += 1

        logger.error(
            "FAILED | Source database not found | %s",
            quran_com_db
        )

        return

    source_name = source["name"]
    source_path = source["path"]

    # Track source
    if source_name == "Quran.com":

        stats["source_quran_com"] += 1

    elif source_name == "alqurandb.com":

        stats["source_alqurandb"] += 1

    elif source_name == "Tartel AI":

        stats["source_tartel"] += 1

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    output_folder = (
        Path(OUTPUT_ROOT)
        / language_pack
    )

    output_database_name = (
        get_output_database_name(
            language,
            translator
        )
    )

    output_path = (
        output_folder
        / output_database_name
    )

    logger.info(
        "Output database: %s",
        output_path
    )

    # --------------------------------------------------------
    # Existing database handling
    # --------------------------------------------------------

    if (
        output_path.exists()
        and not OVERWRITE_EXISTING
    ):

        if output_database_is_complete(
            output_path
        ):

            connection = sqlite3.connect(
                output_path
            )

            try:

                cursor = connection.cursor()

                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {OUTPUT_TABLE}
                    """
                )

                existing_count = (
                    cursor.fetchone()[0]
                )

            finally:

                connection.close()

            logger.info(
                "SKIPPED | Existing database is complete | Rows: %s",
                existing_count
            )

            stats["skipped"] += 1
            stats["total_rows_created"] += existing_count

            return

        else:

            logger.warning(
                "Existing database is incomplete. Recreating: %s",
                output_path
            )

            output_path.unlink()

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    try:

        rows = read_source_rows(
            source_name,
            source_path
        )

    except Exception as error:

        logger.exception(
            "Failed reading source database: %s",
            error
        )

        stats["failed"] += 1

        return

    source_count = len(
        rows
    )

    logger.info(
        "Source rows found: %s",
        source_count
    )

    if source_count == 0:

        logger.warning(
            "Source database is EMPTY: %s",
            source_path
        )

        stats["empty_source"] += 1

        return

    # --------------------------------------------------------
    # Create output DB
    # --------------------------------------------------------

    try:

        create_output_database(
            output_path
        )

        result = insert_rows(
            output_path,
            rows
        )

        inserted = result[
            "inserted"
        ]

        skipped = result[
            "skipped"
        ]

        stats["processed"] += 1
        stats["created"] += 1
        stats["total_rows_created"] += inserted

        logger.info(
            "SUCCESS | Database created"
        )

        logger.info(
            "Source: %s",
            source_name
        )

        logger.info(
            "Source rows: %s",
            source_count
        )

        logger.info(
            "Inserted rows: %s",
            inserted
        )

        logger.info(
            "Skipped rows: %s",
            skipped
        )

        logger.info(
            "Output: %s",
            output_path
        )

        if inserted == source_count:

            logger.info(
                "STATUS: COMPLETE | All rows copied successfully"
            )

        else:

            logger.warning(
                "STATUS: PARTIAL | Source=%s | Inserted=%s | Skipped=%s",
                source_count,
                inserted,
                skipped
            )

    except Exception as error:

        logger.exception(
            "FAILED creating output database: %s",
            error
        )

        stats["failed"] += 1

        # Remove partially created database
        if output_path.exists():

            try:

                output_path.unlink()

                logger.info(
                    "Removed incomplete output database: %s",
                    output_path
                )

            except Exception:

                logger.exception(
                    "Could not remove incomplete database"
                )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "================================================================"
    )

    logger.info(
        "TRANSLATION DATABASE CREATION STARTED"
    )

    logger.info(
        "================================================================"
    )

    logger.info(
        "Mapping JSON: %s",
        MAPPING_JSON
    )

    logger.info(
        "Output root: %s",
        OUTPUT_ROOT
    )

    logger.info(
        "Search priority: Quran.com -> alqurandb.com -> Tartel AI"
    )

    logger.info(
        "Overwrite existing: %s",
        OVERWRITE_EXISTING
    )

    mapping_path = Path(
        MAPPING_JSON
    )

    if not mapping_path.exists():

        logger.error(
            "Mapping JSON does not exist: %s",
            mapping_path
        )

        return

    # --------------------------------------------------------
    # Load mapping JSON
    # --------------------------------------------------------

    try:

        with open(
            mapping_path,
            "r",
            encoding="utf-8"
        ) as file:

            mappings = json.load(
                file
            )

    except Exception as error:

        logger.exception(
            "Failed loading mapping JSON: %s",
            error
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

    stats["total_mappings"] = len(
        mappings
    )

    logger.info(
        "Total mappings found: %s",
        stats["total_mappings"]
    )

    # --------------------------------------------------------
    # Process mappings
    # --------------------------------------------------------

    for index, mapping in enumerate(
        mappings,
        start=1
    ):

        try:

            process_mapping(
                mapping,
                index,
                stats["total_mappings"]
            )

        except Exception as error:

            logger.exception(
                "Unexpected error while processing mapping %s: %s",
                index,
                error
            )

            stats["failed"] += 1

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    logger.info(
        ""
    )

    logger.info(
        "================================================================"
    )

    logger.info(
        "FINAL SUMMARY"
    )

    logger.info(
        "================================================================"
    )

    logger.info(
        "Total mappings:       %s",
        stats["total_mappings"]
    )

    logger.info(
        "Successfully created: %s",
        stats["created"]
    )

    logger.info(
        "Skipped existing:     %s",
        stats["skipped"]
    )

    logger.info(
        "Source not found:     %s",
        stats["source_not_found"]
    )

    logger.info(
        "Empty source DB:      %s",
        stats["empty_source"]
    )

    logger.info(
        "Failed:               %s",
        stats["failed"]
    )

    logger.info(
        "Total rows created:   %s",
        stats["total_rows_created"]
    )

    logger.info(
        ""
    )

    logger.info(
        "SOURCE DATABASE USAGE"
    )

    logger.info(
        "Quran.com:            %s",
        stats["source_quran_com"]
    )

    logger.info(
        "alqurandb.com:        %s",
        stats["source_alqurandb"]
    )

    logger.info(
        "Tartel AI:            %s",
        stats["source_tartel"]
    )

    logger.info(
        ""
    )

    logger.info(
        "Log file: %s",
        LOG_FILE
    )

    logger.info(
        "================================================================"
    )

    logger.info(
        "TRANSLATION DATABASE CREATION FINISHED"
    )

    logger.info(
        "================================================================"
    )


if __name__ == "__main__":

    main()