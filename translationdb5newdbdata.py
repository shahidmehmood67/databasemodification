import json
import os


# ============================================================
# CONFIGURATION
# ============================================================

# Mapping JSON
MAPPING_JSON = (
    r"H:\Other Projects\Python\db\tafseer_reports"
    r"\translation_db_mapping.json"
)

# Generated Kotlin output
OUTPUT_KOTLIN = (
    r"H:\Other Projects\Python\db\tafseer_reports"
    r"\\translation_list_generated.kt"
)


# ============================================================
# LOAD MAPPING JSON
# ============================================================

if not os.path.isfile(MAPPING_JSON):
    raise FileNotFoundError(
        f"Mapping JSON not found:\n{MAPPING_JSON}"
    )


with open(
    MAPPING_JSON,
    "r",
    encoding="utf-8"
) as f:

    mappings = json.load(f)


if not isinstance(mappings, list):
    raise ValueError(
        "Expected translation_db_mapping.json to contain a JSON array."
    )


# ============================================================
# GENERATE KOTLIN
# ============================================================

kotlin_lines = []

kotlin_lines.append(
    "fun getAllTranslationsList(): ArrayList<TranslationBookNewDetail> {"
)

kotlin_lines.append(
    "    return arrayListOf("
)


# ============================================================
# ID GENERATION
#
# Language 1:
#   101, 102, 103...
#
# Language 2:
#   111, 112, 113...
#
# Language 3:
#   121, 122, 123...
#
# Language 4:
#   131, 132...
#
# ============================================================

current_language = None
language_index = -1
translator_index = 0

total_entries = 0
total_languages = 0


for item in mappings:

    language = item.get(
        "language",
        ""
    ).strip()

    translator = item.get(
        "translator",
        ""
    )

    language_pack = item.get(
        "language_pack",
        ""
    ).strip()


    # Convert null translator to empty string
    if translator is None:
        translator = ""

    translator = str(
        translator
    ).strip()


    # ========================================================
    # VALIDATE REQUIRED DATA
    # ========================================================

    if not language:
        print(
            f"WARNING: Skipping entry without language: {item}"
        )
        continue


    if not language_pack:
        print(
            f"WARNING: Skipping {language} because language_pack is empty."
        )
        continue


    # ========================================================
    # CHECK LANGUAGE CHANGE
    # ========================================================

    if language != current_language:

        current_language = language

        language_index += 1

        translator_index = 0

        total_languages += 1


    # ========================================================
    # GENERATE ID
    #
    # language_index = 0 -> 101
    # language_index = 1 -> 111
    # language_index = 2 -> 121
    #
    # translator_index:
    # 0 -> +0
    # 1 -> +1
    # 2 -> +2
    # ========================================================

    translation_id = (
        101
        + (language_index * 10)
        + translator_index
    )


    # ========================================================
    # DEFAULT TRANSLATION
    #
    # First translation of each language = true
    # Other translations = false
    # ========================================================

    is_default = (
        translator_index == 0
    )


    # ========================================================
    # ESCAPE KOTLIN STRINGS
    # ========================================================

    language_kotlin = (
        language
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )

    translator_kotlin = (
        translator
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )

    language_pack_kotlin = (
        language_pack
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )


    # ========================================================
    # ADD KOTLIN ENTRY
    # ========================================================

    kotlin_lines.append(
        "        TranslationBookNewDetail("
    )

    kotlin_lines.append(
        f"            {translation_id},"
    )

    kotlin_lines.append(
        f'            "{language_kotlin}",'
    )

    kotlin_lines.append(
        f'            "{translator_kotlin}",'
    )

    kotlin_lines.append(
        f'            "{language_pack_kotlin}",'
    )

    kotlin_lines.append(
        "            false,"
    )

    kotlin_lines.append(
        "            false,"
    )

    kotlin_lines.append(
        "            false,"
    )

    kotlin_lines.append(
        "            false,"
    )

    kotlin_lines.append(
        f"            {str(is_default).lower()}"
    )

    kotlin_lines.append(
        "        ),"
    )


    translator_index += 1

    total_entries += 1


# ============================================================
# REMOVE LAST COMMA
# ============================================================

if kotlin_lines[-1].strip() == "),":
    kotlin_lines[-1] = "        )"


# ============================================================
# CLOSE KOTLIN FUNCTION
# ============================================================

kotlin_lines.append(
    "    )"
)

kotlin_lines.append(
    "}"
)


# ============================================================
# WRITE KOTLIN FILE
# ============================================================

output_dir = os.path.dirname(
    OUTPUT_KOTLIN
)

if output_dir:
    os.makedirs(
        output_dir,
        exist_ok=True
    )


with open(
    OUTPUT_KOTLIN,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(
            kotlin_lines
        )
    )


# ============================================================
# SUMMARY
# ============================================================

print("=" * 80)
print("KOTLIN TRANSLATION LIST GENERATION FINISHED")
print("=" * 80)

print(
    f"Mapping JSON       : {MAPPING_JSON}"
)

print(
    f"Output Kotlin      : {OUTPUT_KOTLIN}"
)

print(
    f"Languages          : {total_languages}"
)

print(
    f"Translations       : {total_entries}"
)

print("=" * 80)