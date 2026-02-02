import zipfile
import tarfile
import os
import shutil
import time

def extract_recursive(current_path):
    """
    Continually scans and extracts any zip or tar-like archives 
    found at any depth within the current_path.
    """
    # Look at every file/folder in the current directory
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        
        # Skip hidden Mac metadata and our final master folders
        if item.startswith("._") or "__MACOSX" in item or "master" in item:
            continue

        # If it's a directory, dive into it (Recursion)
        if os.path.isdir(item_path):
            extract_recursive(item_path)
            continue

        # If it's a file, check if it's a known archive type
        is_zip = item.lower().endswith((".zip", ".stdf", ".summary"))
        is_tar = item.lower().endswith((".tar", ".tar.gz", ".tgz"))

        if is_zip or is_tar:
            # Create a unique extraction folder to avoid filename collisions
            extract_to = os.path.join(current_path, f"{item}_extracted")
            os.makedirs(extract_to, exist_ok=True)
            
            print(f"Processing archive: {item}")
            try:
                if is_zip:
                    with zipfile.ZipFile(item_path, 'r') as z:
                        z.extractall(extract_to)
                elif is_tar:
                    with tarfile.open(item_path, 'r') as t:
                        t.extractall(extract_to, filter='data')
                
                # Close file and wait for Windows to release the lock before deleting
                time.sleep(0.1)
                os.remove(item_path)
                
                # IMPORTANT: Immediately dive into the newly extracted folder 
                # in case it contains more archives
                extract_recursive(extract_to)
                
            except (zipfile.BadZipFile, tarfile.ReadError):
                # If it's not actually an archive (e.g., a raw .stdf file), 
                # cleanup the empty folder we made and keep the file
                if not os.listdir(extract_to):
                    os.rmdir(extract_to)
            except Exception as e:
                print(f"Error on {item}: {e}")

def organize_files(source_dir, stdf_master, summary_master):
    """
    Scans the fully unzipped tree and copies .stdf and .summary files 
    into their respective master folders.
    """
    print("\n--- Phase 2: Organizing Master Folders ---")
    os.makedirs(stdf_master, exist_ok=True)
    os.makedirs(summary_master, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        # Don't search inside the master folders themselves
        if "master" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.lower().endswith(".stdf"):
                print(f"Copying STDF: {file}")
                shutil.copy2(file_path, os.path.join(stdf_master, file))
            
            elif file.lower().endswith(".summary"):
                print(f"Copying Summary: {file}")
                shutil.copy2(file_path, os.path.join(summary_master, file))

# ==========================================
# SETTINGS
# ==========================================
# r"" prefix is essential for Windows paths
input_zip = r"C:\Users\YourName\Desktop\zipped.zip"
output_workspace = r"C:\Users\YourName\Desktop\Work_Area"

stdf_master_path = os.path.join(output_workspace, "stdf_master")
summary_master_path = os.path.join(output_workspace, "summary_master")

if __name__ == "__main__":
    if not os.path.exists(output_workspace):
        os.makedirs(output_workspace)

    try:
        # Initial extraction to start the process
        print("Initial extraction started...")
        with zipfile.ZipFile(input_zip, 'r') as start_ref:
            start_ref.extractall(output_workspace)

        # Start the recursive chain reaction
        extract_recursive(output_workspace)

        # Move files to their final destination
        organize_files(output_workspace, stdf_master_path, summary_master_path)

        print("\nSUCCESS! All layers unzipped and files sorted.")
    except Exception as e:
        print(f"Critical failure: {e}")
