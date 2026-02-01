# ZIP EXTRACTION UTILITY
# ----------------------
# Description:
# This script performs a recursive extraction of a ZIP file. If the main ZIP
# contains nested ZIP files, the script will automatically detect and unzip 
# them into their own sub-folders until no compressed files remain.

# Key Features:
# - Handles nested ZIP files (unzip-within-unzip).
# - Cross-platform: Works on Windows and macOS.
# - Mac-Safe: Automatically ignores '._' metadata files and '__MACOSX' folders.
# - Clean-up: Deletes original ZIP files after extraction to save space.
# """

import zipfile
import os
import shutil

def extract_nested_zips(target_directory):
    """
    Recursively finds and extracts zip files within a directory, 
    ignoring macOS metadata files and folders.
    """
    while True:
        found_zip = False
        for root, dirs, files in os.walk(target_directory):
            # 1. Skip the __MACOSX resource fork folders entirely
            if "__MACOSX" in root:
                continue
                
            for file in files:
                # 2. Only process real .zip files
                # We specifically skip files starting with '._' (Mac metadata)
                if file.endswith(".zip") and not file.startswith("._"):
                    found_zip = True
                    zip_path = os.path.join(root, file)
                    
                    # Create a folder name based on the zip file name
                    folder_name = os.path.splitext(zip_path)[0]
                    
                    print(f"Unzipping nested file: {file}")
                    
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(folder_name)
                        
                        # Remove the zip file after successful extraction
                        os.remove(zip_path)
                    except zipfile.BadZipFile:
                        print(f"Skipping invalid zip file: {file}")
                        # Move on so we don't get stuck in an infinite loop
                        continue 
        
        # If no more valid zips were found in this pass, we are finished
        if not found_zip:
            break

    # 3. Final Cleanup: Remove any empty __MACOSX folders left behind
    for root, dirs, files in os.walk(target_directory, topdown=False):
        for name in dirs:
            if name == "__MACOSX":
                shutil.rmtree(os.path.join(root, name))

# --- Execution ---

main_zip = "/Users/nusrattazin/Desktop/Nusrat_Office_Code/8520051A.001.zip"
destination = "/Users/nusrattazin/Desktop/Nusrat_Office_Code/Unzipped/"

# Ensure destination exists
if not os.path.exists(destination):
    os.makedirs(destination)

print("Starting main extraction...")
try:
    with zipfile.ZipFile(main_zip, 'r') as initial_ref:
        initial_ref.extractall(destination)

    # Run the recursive function
    extract_nested_zips(destination)
    print("\nSuccess: All nested layers have been extracted and cleaned!")

except FileNotFoundError:
    print(f"Error: Could not find the file at {main_zip}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
