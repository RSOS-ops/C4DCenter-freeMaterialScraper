# C4D Center Material Scraper & Asset Manager (v2.2)

A professional suite for the systematic extraction and management of 3D materials from the C4D Center library. This version features a complete CLI-based configuration wizard and an integrated extraction utility.

> [!WARNING]
> UPDATE YOUR OWN RANDOMIZED INTERVAL TO MIMIC HUMAN-NESS. SUGGESTED IS 3-7 SECONDS. Running at high speeds may result in IP rate-limiting or server-side blocks.

---

## 🚀 Key Features

* **Interactive CLI Wizard:** On startup, the script prompts for download paths, headless preferences, and specific page ranges, removing the need for hardcoded edits.
* **Integrated Extraction Tool:** Includes `extract_assets.py` to batch-extract all downloaded `.zip` files into a single directory using 7-Zip.
* **Real-Time Progress Tracking:** Provides live console updates identifying the specific material currently being processed.
* **Session Summary Report:** Generates a comprehensive breakdown at the end of each run, detailing total materials found, successful downloads, duplicates skipped, and errors encountered.
* **Performance Optimization:** * **Eager Load Strategy:** Interacts with the DOM as soon as the basic structure is ready, rather than waiting for external trackers or ads.
    * **Image Suppression:** Disables image rendering to drastically reduce bandwidth and CPU usage during the crawl.
* **Stealth & Ethics:**
    * **Human-Mimicry Delays:** Features customizable randomized intervals to respect server load and avoid robotic request patterns.
    * **Micro-Action Jitter:** Simulates brief pauses (0.3s – 0.6s) before click actions for enhanced reliability.
* **Intelligent Logic:**
    * **Duplicate Detection:** Scans the target directory and automatically skips materials already present locally.
    * **Robust File-State Validation:** Monitors OS-level file buffers to ensure `.tmp` and `.crdownload` files are fully finalized and renamed before proceeding.

---

## 🛠 Prerequisites

* **Python:** 3.8+
* **Browser:** [Google Chrome](https://www.google.com/chrome/)
* **Extraction:** [7-Zip](https://www.7-zip.org/) (Required for the extraction utility)
* **Drivers:** Managed automatically via `webdriver-manager`.

### Installation
```bash
pip install selenium webdriver-manager``

---

##  Cinema 4D Material Importer (`c4d-importer.py`)

This script imports all extracted materials directly into your Cinema 4D scene, allowing you to easily add them to your permanent Asset Browser library.

### Prerequisites

* **Cinema 4D:** 2024 or newer (tested on 2026.1.0)
* **Extracted Materials:** You must first run the scraper and extraction utility to have `.c4d` material files available

### How to Use

#### Step 1: Run the Import Script

1. Open **Cinema 4D** and create a new empty scene (or open an existing project)
2. Go to **Extensions  Script Manager** (or press `Shift+F11`)
3. Click **File  Open** and select `c4d-importer.py`
4. **Important:** Verify the `PARENT_DIRECTORY` path at the top of the script points to your extracted materials folder (e.g., `C:\Users\YourName\Downloads\C4DCenter-materials\Extracted_Materials`)
5. Click **Execute** to run the script
6. All materials will be imported into your scene's **Material Manager**

#### Step 2: Re-link Missing Textures

After import, the materials will show missing texture warnings because the file paths have changed. To fix this:

1. Go to **Window  Project Asset Inspector**
2. In the Asset Inspector, you will see a list of all missing texture files
3. **Select all missing textures** (click the first one, then `Ctrl+Shift+End` to select all, or `Ctrl+A`)
4. Right-click and choose **Relink Assets...** (or use the Relink button in the toolbar)
5. In the relink dialog, **navigate to your Extracted Materials folder**  this is the parent directory containing all the material subfolders (the same `PARENT_DIRECTORY` path from the script)
6. Enable **"Search Subdirectories"** if available
7. Click **OK**  Cinema 4D will automatically find and relink all textures

#### Step 3: Save Materials to Asset Browser

Once all textures are properly linked:

1. Open the **Asset Browser** (`Shift+F8`)
2. Go to your **Material Manager** and select the materials you want to save
3. **Drag and drop** the materials directly into the Asset Browser
4. Choose a category or create a new one (e.g., "C4D Center Materials")
5. The materials are now **permanently saved** in your Asset Browser and can be used in any future project

### Tips

- Import materials in batches if you have many files to avoid overwhelming the Material Manager
- Create organized folders in your Asset Browser before dragging materials in
- The original `.c4d` files remain in the Extracted Materials folder as backups
- If textures fail to relink, ensure the texture files (.png, .jpg, .exr, etc.) are in the same folders as their corresponding `.c4d` files

### Import Log File

After each import session, the script automatically creates a detailed log file in your `PARENT_DIRECTORY` folder:

- **Filename:** `material_import_log_YYYYMMDD_HHMMSS.txt` (timestamped)
- **Contents:** Complete list of all imported materials, summary statistics, and session details
- **Purpose:** Track what materials were imported and when for your records

** For complete usage instructions, see [c4d-import-howTo.md](c4d-import-howTo.md)**
