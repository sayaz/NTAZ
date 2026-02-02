"""
AGGRESSIVE RECURSIVE ARCHIVE EXTRACTOR
--------------------------------------
Purpose: Deep-dive into all nested .zip and .tar archives regardless of depth.
Output: Organized 'stdf' and 'summary' folders.
"""

import zipfile
import tarfile
import os
import shutil
import time

def extract_all_deep(target_dir):
    """
    Dives into every folder. If it finds a zip or tar, it extracts it
    and then immediately checks the NEWLY extracted folder for more archives.
    """
    # 1. Look for any archives in the current target_dir
    files_found = os.listdir(target_dir)
    
    for file in files_found:
        file_path = os.path.join(target_dir, file)
        
        # Skip Mac metadata
        if file.startswith("._") or "__MACOSX" in file:
            continue
            
        is_archive = False
        # Identify Archive Type
        if file.lower().endswith(".zip"):
            is_archive = True
            archive_type = 'zip'
        elif file.lower().endswith((".tar", ".tar.gz", ".tgz")):
            is_archive = True
            archive_type = 'tar'

        if is_archive:
            # Create a unique folder name for this archive
            # This handles .tar.gz correctly by taking everything before the first dot
            folder_name = os.path.join(target_dir, file.replace('.', '_') + "_extracted")
            
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            print(f"Extracting: {file_path}")
            try:
                if archive_type == 'zip':
                    with zipfile.ZipFile(file_path, 'r') as ref:
                        ref.extractall(folder_name)
                else:
                    with tarfile.open(file_path, 'r') as ref:
                        ref.extractall(folder_name, filter='data')
                
                # Close the handle and wait for Windows to release the lock
                time.sleep(0.2) 
                os.remove(file_path)
                
                # RECURSION: Now dive into the folder we just created to see if IT has zips
                extract_all_deep(folder_name)
                
            except Exception as e:
                print(f"Failed to process {file}: {e}")

    # 2. After checking files, check sub-directories that already existed
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isdir(item_path) and "stdf" not in item and "summary" not in item:
            extract_all_deep(item_path)

def final_sort(search_dir, stdf_master, summary_master):
    """Moves all .stdf and .txt files found anywhere in search_dir to master folders."""
    print("\n--- Starting Final Sort ---")
    os.makedirs(stdf_master, exist_ok=True)
    os.makedirs(summary_master, exist_ok=True)

    for root, dirs, files in os.walk(search_dir):
        # Avoid moving files that are already in the destination
        if "stdf" in root or "summary" in root:
            continue
            
        for file in files:
            source_path = os.path.join(root, file)
            if file.lower().endswith(".stdf"):
                # Move to stdf folder
                shutil.move(source_path, os.path.join(stdf_master, file))
                print(f"Moved to stdf: {file}")
            elif file.lower().endswith(".txt"):
                # Move to summary folder
                shutil.move(source_path, os.path.join(summary_master, file))
                print(f"Moved to summary: {file}")

# ==========================================
# RUN SCRIPT
# ==========================================
# Use 'r' for Windows paths
main_input_file = r"C:\Users\YourName\Desktop\zipped.zip"
working_dir = r"C:\Users\YourName\Desktop\Unzipped_Workspace"

stdf_folder = os.path.join(working_dir, "stdf")
summary_folder = os.path.join(working_dir, "summary")

if __name__ == "__main__":
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    print("--- Phase 1: Initial Extraction ---")
    try:
        # Initial kick-off
        if main_input_file.lower().endswith(".zip"):
            with zipfile.ZipFile(main_input_file, 'r') as initial:
                initial.extractall(working_dir)
        else:
            with tarfile.open(main_input_file, 'r') as initial:
                initial.extractall(working_dir, filter='data')

        print("--- Phase 2: Deep Recursive Extraction ---")
        extract_all_deep(working_dir)

        print("--- Phase 3: Sorting ---")
        final_sort(working_dir, stdf_folder, summary_folder)

        print("\nAll done! Check your 'stdf' and 'summary' folders.")
    except Exception as e:
        print(f"Process failed: {e}")
