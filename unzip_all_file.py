"""
DEEP RECURSIVE ARCHIVE EXTRACTOR (Support for .stdf and .summary)
---------------------------------------------------------------
This version treats .stdf and .summary files as compressed folders.
"""

import zipfile
import tarfile
import os
import shutil
import time

def extract_all_deep(target_dir):
    """
    Dives into every folder. If it finds a zip, tar, stdf, or summary file, 
    it extracts it as an archive.
    """
    files_found = os.listdir(target_dir)
    
    for file in files_found:
        file_path = os.path.join(target_dir, file)
        
        # Skip Mac metadata and already created destination folders
        if file.startswith("._") or "__MACOSX" in file:
            continue
            
        is_archive = False
        archive_type = None

        # Define which extensions should be treated as archives
        if file.lower().endswith(".zip"):
            is_archive, archive_type = True, 'zip'
        elif file.lower().endswith((".tar", ".tar.gz", ".tgz")):
            is_archive, archive_type = True, 'tar'
        # TREAT .STDF AND .SUMMARY AS ARCHIVES
        elif file.lower().endswith((".stdf", ".summary")):
            is_archive, archive_type = True, 'zip' # Assuming these are zip-based

        if is_archive:
            # Create a unique folder name to extract into
            folder_name = os.path.join(target_dir, file.replace('.', '_') + "_extracted")
            os.makedirs(folder_name, exist_ok=True)
            
            print(f"Extracting Archive Folder: {file}")
            try:
                if archive_type == 'zip':
                    # We use a try-except here in case a .stdf is actually a raw file 
                    # and not a compressed folder
                    try:
                        with zipfile.ZipFile(file_path, 'r') as ref:
                            ref.extractall(folder_name)
                        time.sleep(0.2) 
                        os.remove(file_path)
                    except zipfile.BadZipFile:
                        # If it's not a zip, just leave it alone
                        print(f"File {file} looked like an archive but isn't. Skipping.")
                        if not os.listdir(folder_name): os.rmdir(folder_name)
                
                elif archive_type == 'tar':
                    with tarfile.open(file_path, 'r') as ref:
                        ref.extractall(folder_name, filter='data')
                    time.sleep(0.2)
                    os.remove(file_path)
                
                # RECURSION: Dive into the newly created folder
                if os.path.exists(folder_name):
                    extract_all_deep(folder_name)
                
            except Exception as e:
                print(f"Could not process {file}: {e}")

    # Process sub-directories that already existed
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isdir(item_path) and item not in ["stdf", "summary"]:
            extract_all_deep(item_path)

def final_sort(search_dir, stdf_master, summary_master):
    """
    Final pass: Find the ACTUAL data files (.stdf and .txt) 
    and move them to the final folders.
    """
    print("\n--- Final Organizing Phase ---")
    os.makedirs(stdf_master, exist_ok=True)
    os.makedirs(summary_master, exist_ok=True)

    for root, dirs, files in os.walk(search_dir):
        if "stdf_master" in root or "summary_master" in root:
            continue
            
        for file in files:
            source_path = os.path.join(root, file)
            # Match the files inside the unzipped folders
            if file.lower().endswith(".stdf"):
                shutil.move(source_path, os.path.join(stdf_master, file))
            elif file.lower().endswith(".txt"):
                shutil.move(source_path, os.path.join(summary_master, file))

# ==========================================
# CONFIGURATION
# ==========================================
main_input_file = r"C:\Users\YourName\Desktop\zipped.zip"
working_dir = r"C:\Users\YourName\Desktop\Unzipped_Workspace"

# These names must be different from the recursive folder search to avoid loops
stdf_master = os.path.join(working_dir, "stdf_master_files")
summary_master = os.path.join(working_dir, "summary_master_files")

if __name__ == "__main__":
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    print("--- Starting Deep Extraction ---")
    try:
        # Initial kick-off
        with zipfile.ZipFile(main_input_file, 'r') as initial:
            initial.extractall(working_dir)

        extract_all_deep(working_dir)
        final_sort(working_dir, stdf_master, summary_master)

        print("\nAll done! Check your master folders.")
    except Exception as e:
        print(f"Process failed: {e}")
