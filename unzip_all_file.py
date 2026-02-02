"""
UNIVERSAL ARCHIVE EXTRACTOR & SORTER
------------------------------------
- Supports: .zip, .tar, .tar.gz, .tgz
- Features: Recursive extraction, Mac-metadata filtering, Windows-safe file locks.
- Result: Organizes .stdf and .txt files into master folders.
"""

import zipfile
import tarfile
import os
import shutil
import time

def extract_nested_archives(target_directory):
    """Recursively finds and extracts both ZIP and TAR archives."""
    while True:
        found_archive = False
        for root, dirs, files in os.walk(target_directory):
            # Skip hidden macOS metadata folders
            if "__MACOSX" in root:
                continue
                
            for file in files:
                # Skip Mac 'ghost' files
                if file.startswith("._"):
                    continue
                
                zip_path = os.path.join(root, file)
                # Create a destination folder name (removes .zip or .tar.gz)
                # We use a nested split to handle double extensions like .tar.gz
                folder_name = os.path.join(root, file.split('.')[0])
                
                # --- CASE 1: ZIP FILES ---
                if file.lower().endswith(".zip"):
                    found_archive = True
                    print(f"Unzipping: {file}")
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as ref:
                            ref.extractall(folder_name)
                        time.sleep(0.1) # Windows safety pause
                        os.remove(zip_path)
                    except Exception as e:
                        print(f"Error extracting {file}: {e}")

                # --- CASE 2: TAR FILES ---
                elif file.lower().endswith((".tar", ".tar.gz", ".tgz")):
                    found_archive = True
                    print(f"Untarring: {file}")
                    try:
                        with tarfile.open(zip_path, 'r') as ref:
                            # 'filter' is a security feature for modern Python
                            ref.extractall(folder_name, filter='data')
                        time.sleep(0.1) # Windows safety pause
                        os.remove(zip_path)
                    except Exception as e:
                        print(f"Error extracting {file}: {e}")
        
        # If no archives were processed in this pass, we are done
        if not found_archive:
            break

def sort_and_cleanup(search_directory, stdf_dest, summary_dest):
    """Moves specific file types to master folders and removes empty folders."""
    os.makedirs(stdf_dest, exist_ok=True)
    os.makedirs(summary_dest, exist_ok=True)

    print("\nSorting files...")
    for root, dirs, files in os.walk(search_directory):
        # Don't move files that are already in the destination folders
        if os.path.abspath(root).startswith(os.path.abspath(stdf_dest)) or \
           os.path.abspath(root).startswith(os.path.abspath(summary_dest)):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.lower().endswith(".stdf"):
                    shutil.move(file_path, os.path.join(stdf_dest, file))
                elif file.lower().endswith(".txt"):
                    shutil.move(file_path, os.path.join(summary_dest, file))
            except Exception as e:
                print(f"Could not move {file}: {e}")

    # Final Cleanup
    print("Cleaning up empty directories...")
    for root, dirs, files in os.walk(search_directory, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                # Delete __MACOSX or any truly empty folder
                if name == "__MACOSX" or not os.listdir(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
            except:
                pass

# ==========================================
# CONFIGURATION (Edit paths here)
# ==========================================
# Use 'r' before the string to handle Windows backslashes correctly
main_archive = r"C:\Users\YourName\Desktop\8520051A.001.zip"
base_dir = r"C:\Users\YourName\Desktop\Unzipped"

stdf_master = os.path.join(base_dir, "stdf_files")
summary_master = os.path.join(base_dir, "summary_files")

if __name__ == "__main__":
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    print("--- Process Started ---")
    
    # 1. Open the initial file (Check if it's zip or tar)
    try:
        if main_archive.lower().endswith(".zip"):
            with zipfile.ZipFile(main_archive, 'r') as initial:
                initial.extractall(base_dir)
        else:
            with tarfile.open(main_archive, 'r') as initial:
                initial.extractall(base_dir, filter='data')
        
        # 2. Handle nested files
        extract_nested_archives(base_dir)
        
        # 3. Sort the results
        sort_and_cleanup(base_dir, stdf_master, summary_master)
        
        print("\nSUCCESS: All files extracted and sorted.")
        
    except Exception as e:
        print(f"Critical Error: {e}")
