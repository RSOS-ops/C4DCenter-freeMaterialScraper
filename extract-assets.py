import os
import subprocess
import shutil

# --- 1. CONFIGURATION ---
# Path to your 7-Zip executable. 
# Check if yours is in 'C:\Program Files (x86)\7-Zip\7z.exe' instead.
SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"

def run_extractor():
    print("--- 7-Zip Batch Extractor ---")
    
    # Verify 7-Zip exists before asking for paths
    if not os.path.exists(SEVEN_ZIP_PATH):
        print(f"CRITICAL ERROR: 7-Zip not found at: {SEVEN_ZIP_PATH}")
        print("Please locate 7z.exe on your computer and update the SEVEN_ZIP_PATH in this script.")
        return

    # 2. GET PATHS
    source_dir = input("Enter the path where your .zip files are: ").strip().replace('"', '')
    
    if not os.path.exists(source_dir):
        print(f"ERROR: The directory '{source_dir}' does not exist.")
        return

    dest_dir = os.path.join(source_dir, "Extracted_Materials")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination folder: {dest_dir}")

    # 3. IDENTIFY FILES
    zip_files = [f for f in os.listdir(source_dir) if f.endswith('.zip')]
    
    if not zip_files:
        print(f"0 .zip files found in: {source_dir}")
        print("Make sure the folder contains actual .zip files and not just folders.")
        return

    print(f"Found {len(zip_files)} files. Starting extraction...\n")

    # 4. EXTRACTION LOOP
    success_count = 0
    for zip_file in zip_files:
        zip_path = os.path.join(source_dir, zip_file)
        
        # 'x' = extract with paths, '-o' = output dir, '-y' = yes to all
        cmd = [SEVEN_ZIP_PATH, "x", zip_path, f"-o{dest_dir}", "-y"]
        
        print(f"Working on: {zip_file}...", end=" ", flush=True)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK]")
                success_count += 1
            else:
                print("[FAILED]")
                print(f"      Reason: {result.stderr}")
        except Exception as e:
            print(f"[ERROR] {str(e)}")

    print("\n" + "="*30)
    print(f"Extraction Finished.")
    print(f"Successfully extracted: {success_count} of {len(zip_files)}")
    print(f"Destination: {dest_dir}")
    print("="*30)

if __name__ == "__main__":
    run_extractor()
    input("\nPress Enter to close...") # Keeps the window open if you double-click the file