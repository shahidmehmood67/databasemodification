import os
import subprocess
import shutil

def bytes_to_kb(b):
    return f"{b/1024:.0f} KB"

def optimize_pngs(folder_path):
    optipng = shutil.which("optipng")
    if optipng is None:
        print("❌ optipng not found on PATH. Please install it first.")
        return

    print(f"🔍 Searching for PNG files in: {folder_path}\n")

    for root, _, files in os.walk(folder_path):  # recursive
        for file in files:
            if file.lower().endswith(".png"):
                file_path = os.path.join(root, file)
                before = os.path.getsize(file_path)

                # -o7 = max effort (slowest, best compression)
                # -strip safe = remove non-essential chunks safely (keeps color profile/gamma)
                # subprocess.run([optipng, "-o7", "-strip", "safe", "-quiet", IMAGE_PATH], check=True)
                # subprocess.run([optipng, "-o7", "-quiet", IMAGE_PATH], check=True)
                # subprocess.run([optipng, "-o7", "-strip", "all", "-quiet", IMAGE_PATH], check=True)

                # Run optipng with max effort, strip metadata
                try:
                    subprocess.run(
                        [optipng, "-o7", "-strip", "all", "-quiet", file_path],
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Failed on {file_path}: {e}")
                    continue

                after = os.path.getsize(file_path)
                print(f"✅ {file} : {bytes_to_kb(before)} → {bytes_to_kb(after)}")

    print("\n🎉 Optimization completed.")

if __name__ == "__main__":
    # 👉 Change this path to your folder
    FOLDER = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\Pages\MOD2Compress\usmani\assets2"
    optimize_pngs(FOLDER)
