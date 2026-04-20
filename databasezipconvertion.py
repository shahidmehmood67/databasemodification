import os
import zipfile

# Root Translations folder
TRANSLATIONS_DIR = r"E:\QuranSqlAllData\GwalQuran\CMP\Translations"

# Output folder (you can change if needed)
OUTPUT_DIR = TRANSLATIONS_DIR

# Logging
total_folders = 0
processed = 0
skipped = 0
log_details = []

for folder_name in os.listdir(TRANSLATIONS_DIR):
    folder_path = os.path.join(TRANSLATIONS_DIR, folder_name)

    if not os.path.isdir(folder_path):
        continue

    total_folders += 1

    assets_path = os.path.join(folder_path, "src", "main", "assets")

    # Check if assets folder exists
    if not os.path.exists(assets_path):
        skipped += 1
        log_details.append(f"{folder_name} -> SKIPPED (no assets folder)")
        continue

    # Get all files inside assets
    files = [
        f for f in os.listdir(assets_path)
        if os.path.isfile(os.path.join(assets_path, f))
    ]

    if not files:
        skipped += 1
        log_details.append(f"{folder_name} -> SKIPPED (no files in assets)")
        continue

    zip_name = f"{folder_name}.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(assets_path, file)

                # Add file WITHOUT folder structure
                zipf.write(file_path, arcname=file)

        processed += 1
        log_details.append(f"{folder_name} -> SUCCESS ({len(files)} files)")

    except Exception as e:
        skipped += 1
        log_details.append(f"{folder_name} -> ERROR ({str(e)})")

# Final Summary
print("\n===== PROCESS SUMMARY =====")
print(f"Total folders: {total_folders}")
print(f"Processed (ZIP created): {processed}")
print(f"Skipped/Errors: {skipped}")

print("\nDetails:")
for log in log_details:
    print(log)