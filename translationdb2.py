import os
import re
import json

# ============================================================
# CONFIGURATION
# ============================================================

# Root containing language packs
ROOT_DIR = r"H:\CodersInsightWorkSpace\Gwal Apps\Al Quran\Quran"

# Quran.com translation databases
QURAN_COM_DIR = r"E:\QuranSqlAllData\DB Quran.com\databases\translations"

# Output folder
OUTPUT_ROOT = r"H:\Other Projects\Python\db\tafseer_reports"

# Output JSON file
OUTPUT_JSON = os.path.join(
    OUTPUT_ROOT,
    "translation_db_mapping.json"
)


# ============================================================
# KOTLIN TRANSLATION DATA
# ============================================================

TRANSLATIONS = [
    (202, "Albanian", "Hasan Nahi", "on_lang_pack_albanian"),
    (207, "Azerbaijani", "Musayev", "on_lang_pack_azerbaijani"),
    (208, "Bangla", "", "on_lang_pack_bangla"),
    (209, "Bosnian", "Korkut", "on_lang_pack_bosnian"),
    (212, "Bulgarian", "Version 1", "on_lang_pack_bulgarian"),
    (214, "Chinese", "Simplified", "on_lang_pack_chinese"),
    (215, "Czeck", "Hrbek", "on_lang_pack_czeck"),
    (217, "Dutch", "Version 1", "on_lang_pack_dutch"),
    (219, "English", "A. J. Arberry", "on_lang_pack_english"),
    (229, "English", "Pickthall", "on_lang_pack_english"),
    (230, "English", "Shakir", "on_lang_pack_english"),
    (231, "English", "Transliteration", "on_lang_pack_english"),
    (232, "English", "Yusuf Ali", "on_lang_pack_english"),
    (233, "Finnish", "", "on_lang_pack_finnish"),
    (235, "French", "Hamidullah", "on_lang_pack_french"),
    (236, "German", "Abu Rida Muhammad", "on_lang_pack_german"),
    (237, "German", "Bubenheim Elyas", "on_lang_pack_german"),
    (239, "German", "Zaidan", "on_lang_pack_german"),
    (240, "Hausa", "", "on_lang_pack_hausa"),
    (241, "Indonesian", "", "on_lang_pack_indonesian"),
    (243, "Italian", "Piccardo", "on_lang_pack_italian"),
    (244, "Japanese", "", "on_lang_pack_japanese"),
    (245, "Korean", "", "on_lang_pack_korean"),
    (246, "Kurdî", "", "on_lang_pack_kurdi"),
    (247, "Malay", "", "on_lang_pack_malay"),
    (248, "Malayalam", "", "on_lang_pack_malayalam"),
    (249, "Maranao", "Guro Alim Saromantang", "on_lang_pack_maranao"),
    (250, "Norwegian", "Einar Berg", "on_lang_pack_norwegian"),
    (251, "Persian", "الهی قمشه  ای", "on_lang_pack_persian"),
    (252, "Persian", "حسین انصاریان", "on_lang_pack_persian"),
    (253, "Persian", "مکارم شیرازی", "on_lang_pack_persian"),
    (254, "Poland", "Bielawskiego", "on_lang_pack_poland"),
    (256, "Portuguese", "El Hayek", "on_lang_pack_portuguese"),
    (258, "Romanian", "George Grigore", "on_lang_pack_romanian"),
    (260, "Russian", "Валерия Порохова", "on_lang_pack_russian"),
    (261, "Russian", "М. Н.О. Османов", "on_lang_pack_russian"),
    (262, "Russian", "Эльмир Кулиев", "on_lang_pack_russian"),
    (263, "Somali", "Al Barwani", "on_lang_pack_somali"),
    (264, "Spanish", "Cortes", "on_lang_pack_spanish"),
    (265, "Swahili", "", "on_lang_pack_swahili"),
    (266, "Swedish", "Rashad Kalifa", "on_lang_pack_swedish"),
    (267, "Tamil", "", "on_lang_pack_tamil"),
    (268, "Tatar", "Yakub Ibn Nugman", "on_lang_pack_tatar"),
    (269, "Thai", "", "on_lang_pack_thai"),
    (278, "Turkish", "Diyanet", "on_lang_pack_turkish"),
    (284, "Turkish", "Elmalılı Hamdi Yazır", "on_lang_pack_turkish"),
    (295, "Turkish", "Süleyman Ateş", "on_lang_pack_turkish"),
    (301, "Urdu", "Ahmed Ali", "on_lang_pack_urdu"),
    (302, "Urdu", "احمد رضا خان", "on_lang_pack_urdu"),
    (303, "Urdu", "جالندہری", "on_lang_pack_urdu"),
    (304, "Uzbek", "Мухаммад Содик", "on_lang_pack_uzbek"),
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_language_pack_databases(language_pack):
    """
    Find all .sqlite databases inside:

    ROOT_DIR/
        language_pack/
            src/main/assets/
    """

    assets_path = os.path.join(
        ROOT_DIR,
        language_pack,
        "src",
        "main",
        "assets"
    )

    if not os.path.isdir(assets_path):
        return []

    databases = []

    for file_name in sorted(os.listdir(assets_path)):
        if file_name.lower().endswith(".sqlite"):
            databases.append(file_name)

    return databases


def get_quran_com_databases():
    """
    Get all Quran.com translation databases.
    """

    if not os.path.isdir(QURAN_COM_DIR):
        print(f"[ERROR] Quran.com directory not found:")
        print(QURAN_COM_DIR)
        return []

    databases = []

    for file_name in sorted(os.listdir(QURAN_COM_DIR)):
        if file_name.lower().endswith(".db"):
            databases.append(file_name)

    return databases


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_ROOT, exist_ok=True)


# ============================================================
# SCAN QURAN.COM DATABASES
# ============================================================

quran_com_databases = get_quran_com_databases()

print("=" * 80)
print("Quran.com Translation Databases")
print("=" * 80)

for db in quran_com_databases:
    print(f"  {db}")

print(f"\nTotal Quran.com databases: {len(quran_com_databases)}")


# ============================================================
# BUILD MAPPING
# ============================================================

mapping = []

print("\n" + "=" * 80)
print("Building Translation Mapping")
print("=" * 80)

for translation_id, language, translator, language_pack in TRANSLATIONS:

    source_databases = find_language_pack_databases(
        language_pack
    )

    # If language pack contains multiple SQLite files,
    # each one is stored in the JSON.
    if source_databases:
        source_db = source_databases
    else:
        source_db = []

    item = {
        "id": translation_id,
        "language": language,
        "translator": translator,
        "language_pack": language_pack,
        "source_db": source_db,
        "quran_com_db": None
    }

    mapping.append(item)

    print(
        f"{translation_id:<5} | "
        f"{language:<15} | "
        f"{translator:<30} | "
        f"Source DBs: {len(source_databases)}"
    )


# ============================================================
# WRITE JSON
# ============================================================

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mapping,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("Finished")
print("=" * 80)

print(f"Translations      : {len(mapping)}")
print(f"Quran.com DBs     : {len(quran_com_databases)}")
print(f"Output JSON        : {OUTPUT_JSON}")

print("\nNext step:")
print("Open translation_db_mapping.json")
print("and manually fill the 'quran_com_db' field.")