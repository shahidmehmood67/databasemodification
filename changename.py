import os
import re

# ==== CONFIG ====
folder_path = r"D:\Assets\Assets Quran\full indopak gwal\assetpacks\on_demand_quran\520109\520109\assets"  # change this to your folder path

pattern = re.compile(r"^(page)(\d+)(_optimized)(\.\w+)$", re.IGNORECASE)

for filename in os.listdir(folder_path):
    match = pattern.match(filename)
    if match:
        prefix, num_str, suffix, ext = match.groups()
        num = int(num_str) - 1  # subtract 1 from the number
        new_name = f"{prefix}{num:03d}{ext}"
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)

        print(f"Renaming: {filename} -> {new_name}")
        os.rename(old_path, new_path)

print("Renaming completed.")
