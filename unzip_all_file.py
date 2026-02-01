"""
ZIP EXTRACTION & FILE SORTER
----------------------------
1. Recursively unzips all folders (handling nested zips).
2. Cleans up macOS metadata (.__MACOSX and ._ files).
3. Sorts .stdf and .txt files into dedicated master folders.
4. Deletes empty source folders after sorting.
"""

import zipfile
import os
import shutil

def extract_nested_zips(target_directory):
    """Recursively finds and extracts all zip files."""
    while True:
        found_zip = False
        for root, dirs, files in os.walk(target_directory):
            if "__MACOSX" in root:
                continue
            for file in files:
                if file.endswith(".zip") and not file.startswith("._"):
                    found_zip = True
                    zip_path = os.path.join(root, file)
                    folder_name = os.path.splitext(zip_path)[0]
                    
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(folder_name)
                        os.remove(zip_path)
                    except zipfile.BadZipFile:
                        pass 
        if not found_zip:
            break

def sort_and_cleanup(search_directory, stdf_dest, summary_dest):
    """Moves specific file types to destination folders and cleans up."""
    
    # Create the master destination folders if they don't exist
    for path in [stdf_dest, summary_dest]:
        if not os.path.exists(path):
            os.makedirs(path)

    print("Sorting files into master folders...")
    
    for root, dirs, files in os.walk(search_directory):
        # Prevent the script from moving files that are already in the destination
        if root.startswith(stdf_dest) or root.startswith(summary_dest):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Move STDF files
            if file.lower().endswith(".stdf"):
                shutil.move(file_path, os.path.join(stdf_dest, file))
                print(f"Moved STDF: {file}")
                
            # Move Summary (txt) files
            elif file.lower().endswith(".txt"):
                shutil.move(file_path, os.path.join(summary_dest, file))
                print(f"Moved Summary: {file}")

    # Final Cleanup: Remove empty directories left behind
    print("Cleaning up empty folders...")
    for root, dirs, files in os.walk(search_directory, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            if name == "__MACOSX":
                shutil.rmtree(dir_path)
            elif not os.listdir(dir_path): # If folder is empty
                os.rmdir(dir_path)

# ==========================================
# CONFIGURATION
# ==========================================
main_zip = "/Users/nusrattazin/Desktop/Nusrat_Office_Code/8520051A.001.zip"
base_dir = "/Users/nusrattazin/Desktop/Nusrat_Office_Code/Unzipped/"

# New folders for sorted results
stdf_master = os.path.join(base_dir, "stdf_files")
summary_master = os.path.join(base_dir, "summary_files")

if __name__ == "__main__":
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    print("--- Starting Extraction ---")
    with zipfile.ZipFile(main_zip, 'r') as initial_ref:
        initial_ref.extractall(base_dir)

    extract_nested_zips(base_dir)
    
    print("\n--- Starting Sorting ---")
    sort_and_cleanup(base_dir, stdf_master, summary_master)
    
    print("\nProcess Complete! Your files are organized.")
