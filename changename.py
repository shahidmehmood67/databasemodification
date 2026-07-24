import os
import re

folder_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\Greentech\com.greentech.quran\files\mushaf\naskh\width_1152"  # change this to your folder path

pattern = re.compile(r"^(page)(\d{3})(\.\w+)$", re.IGNORECASE)

# Step 1: Rename all matching files to a temporary name to avoid conflicts
for filename in os.listdir(folder_path):
    match = pattern.match(filename)
    if match:
        old_path = os.path.join(folder_path, filename)
        tmp_name = "tmp_" + filename
        tmp_path = os.path.join(folder_path, tmp_name)
        print(f"Temporarily renaming: {filename} -> {tmp_name}")
        os.rename(old_path, tmp_path)

# Step 2: Rename from temporary names to final names with decremented page number
tmp_pattern = re.compile(r"^tmp_(page)(\d{3})(\.\w+)$", re.IGNORECASE)

for filename in os.listdir(folder_path):
    match = tmp_pattern.match(filename)
    if match:
        prefix, num_str, ext = match.groups()
        num = int(num_str) - 1  # decrement page number by 1
        if num < 0:
            print(f"Skipping {filename} because decrement results in negative number.")
            continue
        new_name = f"{prefix}{num:03d}{ext}"
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)
        print(f"Renaming final: {filename} -> {new_name}")
        os.rename(old_path, new_path)

print("Decrement renaming completed.")


