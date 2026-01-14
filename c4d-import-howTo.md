# Cinema 4D Material Importer - Complete Guide

## Overview

The `c4d-importer.py` script automates the process of importing downloaded C4D Center materials into your Cinema 4D scene. It processes all `.c4d` material files from your extracted materials folder and adds them to your current scene's Material Manager.

---

## Prerequisites

Before using this script, ensure you have:

* **Cinema 4D:** Version 2024 or newer (tested and optimized for C4D 2026.1.0)
* **Extracted Materials:** Downloaded materials must be extracted using the `extract-assets.py` utility
* **Active Scene:** An open Cinema 4D scene (can be empty or an existing project)

---

## Configuration

### Step 1: Set the Materials Folder Path

1. Open `c4d-importer.py` in a text editor
2. Locate line 7: `PARENT_DIRECTORY = r"C:\Users\tx3so\Downloads\C4DCenter-materials\Extracted_Materials"`
3. Update this path to match your extracted materials location
4. **Important:** Use the parent folder that contains all the individual material subfolders

**Example:**
```python
PARENT_DIRECTORY = r"C:\Users\YourName\Downloads\C4DCenter-materials\Extracted_Materials"
```

---

## Usage Instructions

### Step 1: Prepare Cinema 4D

1. **Launch Cinema 4D**
2. **Create a new scene** or open an existing project where you want to import materials
3. Navigate to **Extensions → Script Manager** (or press `Shift + F11`)

### Step 2: Load and Execute the Script

1. In the Script Manager, click **File → Open**
2. Browse to and select `c4d-importer.py`
3. **Verify** the `PARENT_DIRECTORY` path at the top of the script is correct
4. Click **Execute** (or press `Ctrl + R`)

### Step 3: Monitor the Import Process

The script will display real-time progress in the Script Manager console:

```
--- Material Import to Current Scene ---
[INFO] Source: C:\Users\tx3so\Downloads\C4DCenter-materials\Extracted_Materials
[INFO] Target: Untitled.c4d
[INFO] Found 89 material file(s) to process

[1/89] Large_Concrete_Surface_09.c4d
  [INFO] Found 1 material(s)
    ✓ Large Concrete Surface 09
[2/89] Metal_Rusty_Panel.c4d
  [INFO] Found 1 material(s)
    ✓ Metal Rusty Panel
...
```

### Step 4: Review Import Summary

When complete, you'll see a summary:

```
============================================================
              IMPORT SUMMARY
============================================================
  Files Processed:       89
  Materials Imported:    89
  Errors:                0
============================================================

[SUCCESS] Materials have been imported to your current scene!
[INFO] Check the Material Manager to see all imported materials.
[LOG] Import log saved to: C:\...\material_import_log_20260114_153045.txt
```

---

## Import Log File

### What is the Log File?

After each import session, the script automatically generates a detailed log file saved to your `PARENT_DIRECTORY` folder.

### Log File Details

* **Location:** Same folder as your extracted materials (`PARENT_DIRECTORY`)
* **Filename Format:** `material_import_log_YYYYMMDD_HHMMSS.txt`
* **Purpose:** Track which materials were imported and when

### Log File Contents

The log includes:
- Date and time of import
- Source folder path
- Target Cinema 4D scene name
- Summary statistics (files processed, materials imported, errors)
- **Complete list of all imported materials** with their source files

**Example Log:**
```
============================================================
       C4D CENTER MATERIAL IMPORT LOG
============================================================
Date: 2026-01-14 15:30:45
Source: C:\Users\tx3so\Downloads\C4DCenter-materials\Extracted_Materials
Target Scene: Untitled.c4d
============================================================

Files Processed: 89
Materials Imported: 89
Errors: 0

------------------------------------------------------------
IMPORTED MATERIALS:
------------------------------------------------------------
  • Large Concrete Surface 09 (from: Large_Concrete_Surface_09.c4d)
  • Metal Rusty Panel (from: Metal_Rusty_Panel.c4d)
  • Wood Planks Dark (from: Wood_Planks_Dark.c4d)
  ...
============================================================
```

---

## Fixing Missing Textures

After import, materials will show missing texture warnings because file paths have changed. Here's how to fix this:

### Step 1: Open Project Asset Inspector

1. In Cinema 4D, go to **Window → Project Asset Inspector**
2. You'll see a list of all assets used in your scene
3. Missing textures will be flagged with warning icons

### Step 2: Relink All Textures

1. **Select all missing textures:**
   - Click the first missing texture
   - Press `Ctrl + Shift + End` to select all, or `Ctrl + A` to select all assets
   
2. **Start the relink process:**
   - Right-click on the selected textures
   - Choose **Relink Assets...** from the context menu
   - Alternatively, click the **Relink** button in the Asset Inspector toolbar

3. **Navigate to materials folder:**
   - In the relink dialog, browse to your `PARENT_DIRECTORY` folder
   - This is the same folder path you configured in the script
   
4. **Enable subdirectory search:**
   - Check the **"Search Subdirectories"** or **"Include Subfolders"** option
   - This ensures Cinema 4D searches all material subfolders
   
5. **Execute relink:**
   - Click **OK** or **Relink**
   - Cinema 4D will automatically find and reconnect all texture files

### Step 3: Verify Textures

- Check the Asset Inspector - warning icons should disappear
- Inspect a few materials in the Material Editor to confirm textures loaded correctly
- Render a test scene if desired to verify material appearance

---

## Saving Materials to Asset Browser

Once textures are properly linked, save materials to your Asset Browser for permanent access:

### Step 1: Prepare Asset Browser

1. Open **Asset Browser** (`Shift + F8`)
2. Create a new category for organization:
   - Right-click in the category tree
   - Select **New Category**
   - Name it (e.g., "C4D Center Materials", "Downloaded Materials", etc.)

### Step 2: Transfer Materials

1. Open the **Material Manager** (if not visible: `Shift + F3`)
2. Select materials you want to save:
   - `Ctrl + A` to select all
   - Or `Ctrl + Click` to select specific materials
3. **Drag and drop** selected materials into your Asset Browser category

### Step 3: Organize (Optional)

- Create subcategories (e.g., "Concrete", "Metal", "Wood")
- Drag materials into appropriate subcategories
- Rename materials if desired for better organization

### Step 4: Cleanup

After saving to Asset Browser:
- You can safely **delete materials from the current scene** if not needed
- The original `.c4d` files remain in your Extracted_Materials folder as backups
- Materials in the Asset Browser are now permanently available for all projects

---

## Tips & Best Practices

### Performance Tips

- **Import in batches:** If you have hundreds of materials, import them in smaller groups to avoid overwhelming the Material Manager
- **Use a dedicated import scene:** Create an empty scene specifically for importing, then transfer to Asset Browser
- **Close unused materials:** After saving to Asset Browser, remove them from the scene to reduce memory usage

### Organization Tips

- **Create descriptive categories** in Asset Browser before importing
- **Use consistent naming** for materials and categories
- **Tag materials** with keywords in Asset Browser for easier searching
- **Review the log file** to track what was imported in each session

### Troubleshooting

**Problem:** Script says "No active document found"
- **Solution:** Make sure Cinema 4D has an open scene before running the script

**Problem:** "Path does not exist" error
- **Solution:** Verify the `PARENT_DIRECTORY` path in line 7 is correct and exists on your system

**Problem:** Materials import but all textures are missing
- **Solution:** Ensure texture files (.png, .jpg, .exr, etc.) are in the same folders as the `.c4d` files
- **Solution:** Check that the extracted materials folders weren't moved after extraction

**Problem:** Some materials won't relink
- **Solution:** Manually locate the texture files and relink individually
- **Solution:** Check if texture files were corrupted during download/extraction

**Problem:** Script runs very slowly
- **Solution:** Reduce the number of materials by organizing them into subfolders and importing one subfolder at a time
- **Solution:** Close other applications to free up system resources

---

## Workflow Summary

```
1. Download materials using C4DCenter-materialScraper-1.py
   ↓
2. Extract materials using extract-assets.py
   ↓
3. Configure PARENT_DIRECTORY in c4d-importer.py
   ↓
4. Open Cinema 4D and create/open a scene
   ↓
5. Run c4d-importer.py in Script Manager
   ↓
6. Open Project Asset Inspector and relink textures
   ↓
7. Save materials to Asset Browser
   ↓
8. Review import log file
   ↓
9. Materials now available for all projects!
```

---

## File Locations Reference

| Item | Default Location |
|------|-----------------|
| Script File | `c4d-importer.py` |
| Extracted Materials | `C:\Users\[User]\Downloads\C4DCenter-materials\Extracted_Materials\` |
| Import Log Files | Same as Extracted Materials folder |
| Asset Browser | Cinema 4D Preferences → Asset Browser (internal database) |

---

## Support & Additional Notes

- The script processes **all** `.c4d` files found in the `PARENT_DIRECTORY` and its subfolders
- Each import session creates a **unique timestamped log file** for record-keeping
- Materials are **cloned**, not moved - original files remain untouched
- The script is **non-destructive** - it only adds materials to your scene
- You can run the script multiple times on the same folder (materials will be duplicated in the scene)

For issues or questions, refer to the main README.md or check the import log file for detailed information about what was imported.
