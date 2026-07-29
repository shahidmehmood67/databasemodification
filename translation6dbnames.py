import os

ROOT_DIR = r"H:\Other Projects\Python\db\tafseer_newdb"

for folder_name in sorted(os.listdir(ROOT_DIR)):
    folder_path = os.path.join(ROOT_DIR, folder_name)

    if not folder_name.startswith("on_lang_pack_"):
        continue

    if not os.path.isdir(folder_path):
        continue

    print(folder_name)

    for file_name in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith(
            (".sqlite", ".sqlite3", ".db")
        ):
            print(f"    {file_name}")

    print()