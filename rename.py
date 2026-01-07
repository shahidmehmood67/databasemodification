import os
import re

# Hardcoded folder path - UPDATE THIS PATH
FOLDER_PATH = r"H:\CodersInsightWorkSpace\Multiplatform\Gwal Apps\Al Quran CMP\Al Quran\Quran\on_demand_quran_indopak\src\main\assets\indopak"

def extract_page_number(filename):
    """Extract page number from filename like 'page001.ext' or 'page1.ext'"""
    match = re.search(r'page(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def get_file_extension(filename):
    """Get file extension including the dot"""
    return os.path.splitext(filename)[1]


def rename_files_increment():
    """Rename files by incrementing page numbers, starting from the last file"""

    # Check if folder exists
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Folder '{FOLDER_PATH}' does not exist!")
        return

    # Get all files in the folder
    all_files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]

    # Filter files that match the pattern 'pageXXX'
    page_files = []
    for filename in all_files:
        page_num = extract_page_number(filename)
        if page_num is not None:
            page_files.append((page_num, filename))

    if not page_files:
        print("No files matching 'pageXXX' pattern found!")
        return

    # Sort by page number in descending order (start from last)
    page_files.sort(reverse=True, key=lambda x: x[0])

    print(f"Found {len(page_files)} files to rename")
    print("Starting renaming process from last to first...\n")

    renamed_count = 0

    # Process files from highest to lowest page number
    for page_num, old_filename in page_files:
        old_path = os.path.join(FOLDER_PATH, old_filename)

        # Get file extension
        extension = get_file_extension(old_filename)

        # Create new filename with incremented page number (padded to 3 digits)
        new_page_num = page_num + 1
        new_filename = f"page{new_page_num:03d}{extension}"
        new_path = os.path.join(FOLDER_PATH, new_filename)

        try:
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {old_filename} -> {new_filename}")
            renamed_count += 1
        except Exception as e:
            print(f"Error renaming {old_filename}: {str(e)}")

    print(f"\nRenaming complete! {renamed_count} files renamed successfully.")


if __name__ == "__main__":
    print("=" * 60)
    print("FILE RENAMER - Increment Page Numbers")
    print("=" * 60)
    print(f"Target folder: {FOLDER_PATH}\n")

    # Ask for confirmation
    response = input("This will rename files in the folder. Continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        rename_files_increment()
    else:
        print("Operation cancelled.")