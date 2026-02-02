import zipfile
import tarfile
import gzip
import os
import shutil
import time

def extract_recursive(current_path):
    """
    Scans every file. If it's a zip, tar, or gz, it decompresses it.
    If a new folder is created, it immediately dives into it.
    """
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        
        # Skip Mac metadata and final master folders
        if item.startswith("._") or "__MACOSX" in item or "master" in item:
            continue

        if os.path.isdir(item_path):
            extract_recursive(item_path)
            continue

        item_lower = item.lower()
        processed = False

        # --- 1. HANDLE GZIP (.gz) ---
        if item_lower.endswith(".gz"):
            # Remove .gz extension for the new filename
            decompressed_path = item_path[:-3] 
            print(f"Decompressing GZ: {item}")
            try:
                with gzip.open(item_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                time.sleep(0.1)
                os.remove(item_path)
                processed = True
            except Exception as e:
                print(f"GZ Error on {item}: {e}")

        # --- 2. HANDLE ZIP & CUSTOM EXTENSIONS (.zip, .stdf, .summary) ---
        elif item_lower.endswith((".zip", ".stdf", ".summary")):
            extract_to = os.path.join(current_path, f"{item}_extracted")
            try:
                with zipfile.ZipFile(item_path, 'r') as z:
                    os.makedirs(extract_to, exist_ok=True)
                    z.extractall(extract_to)
                time.sleep(0.1)
                os.remove(item_path)
                extract_recursive(extract_to) # Dive into new folder
                processed = True
            except (zipfile.BadZipFile, PermissionError):
                # If it's a raw file (not a zip), we just leave it alone
                if os.path.exists(extract_to) and not os.listdir(extract_to):
                    os.rmdir(extract_to)

        # --- 3. HANDLE TAR (.tar, .tar.gz, .tgz) ---
        elif item_lower.endswith((".tar", ".tar.gz", ".tgz")):
            extract_to = os.path.join(current_path, f"{item}_extracted")
            try:
                with tarfile.open(item_path, 'r') as t:
                    os.makedirs(extract_to, exist_ok=True)
                    t.extractall(extract_to, filter='data')
                time.sleep(0.1)
                os.remove(item_path)
                extract_recursive(extract_to) # Dive into new folder
                processed = True
            except Exception as e:
                print(f"TAR Error on {item}: {e}")

def organize_files(source_dir, stdf_master, summary_master):
    """
    Scans the final tree for .stdf and .summary files.
    """
    print("\n--- Phase 2: Organizing Master Folders ---")
    os.makedirs(stdf_master, exist_ok=True)
    os.makedirs(summary_master, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        if "master" in root: continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Use copy2 to keep file dates/metadata
            if file.lower().endswith(".stdf"):
                shutil.copy2(file_path, os.path.join(stdf_master, file))
            elif file.lower().endswith(".summary"):
                shutil.copy2(file_path, os.path.join(summary_master, file))

# ==========================================
# SETTINGS
# ==========================================
input_zip = r"C:\\Users\\TaziN\\Downloads\zipfiles.zip"
output_workspace = r"C:\\TaziN\\Downloads\\Unzipped"

stdf_master_path = os.path.join(output_workspace, "stdf_master")
summary_master_path = os.path.join(output_workspace, "summary_master")

if __name__ == "__main__":
    if not os.path.exists(output_workspace):
        os.makedirs(output_workspace)

    try:
        print("Initial extraction...")
        # Start by unzipping the main container
        with zipfile.ZipFile(input_zip, 'r') as start_ref:
            start_ref.extractall(output_workspace)

        # Start the recursive chain
        extract_recursive(output_workspace)

        # Move to master folders
        organize_files(output_workspace, stdf_master_path, summary_master_path)

        print("\nSUCCESS! Everything is decompressed and sorted.")
    except Exception as e:
        print(f"Critical failure: {e}")
