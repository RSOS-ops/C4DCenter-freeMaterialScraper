import c4d
import os
from datetime import datetime

# --- CONFIGURATION ---
# [IMPORTANT] Update this path to your actual Extracted_Materials folder
PARENT_DIRECTORY = r"C:\Users\tx3so\Downloads\C4DCenter-materials\Extracted_Materials"


def import_materials_to_scene():
    """Import all materials from .c4d files into the currently open Cinema 4D scene."""
    print("--- Material Import to Current Scene ---")
    print(f"[INFO] Source: {PARENT_DIRECTORY}")
    
    if not os.path.exists(PARENT_DIRECTORY):
        print(f"[ERROR] Path does not exist: {PARENT_DIRECTORY}")
        return
    
    # Get the active document
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        print("[ERROR] No active document found. Please open a scene first.")
        return
    
    print(f"[INFO] Target: {doc.GetDocumentName()}")
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"material_import_log_{timestamp}.txt"
    log_path = os.path.join(PARENT_DIRECTORY, log_filename)
    imported_materials = []
    
    stats = {"files_processed": 0, "materials_imported": 0, "errors": 0}
    
    # Collect all .c4d files
    c4d_files = []
    for root, dirs, files in os.walk(PARENT_DIRECTORY):
        for file in files:
            if file.lower().endswith(".c4d"):
                c4d_files.append(os.path.join(root, file))
    
    total_files = len(c4d_files)
    print(f"[INFO] Found {total_files} material file(s) to process\n")
    
    for idx, file_path in enumerate(c4d_files, 1):
        filename = os.path.basename(file_path)
        print(f"[{idx}/{total_files}] {filename}")
        
        # Load the source document
        source_doc = None
        try:
            source_doc = c4d.documents.LoadDocument(
                file_path,
                c4d.SCENEFILTER_MATERIALS | c4d.SCENEFILTER_MERGESCENE,
                None
            )
        except Exception as e:
            print(f"  [ERROR] Load failed: {e}")
            stats["errors"] += 1
            continue
        
        if not source_doc:
            print(f"  [ERROR] Could not load document")
            stats["errors"] += 1
            continue
        
        try:
            # Set document path to help resolve texture paths
            source_doc.SetDocumentPath(os.path.dirname(file_path))
            
            # Get all materials from the source document
            materials = source_doc.GetMaterials()
            mat_count = len(materials) if materials else 0
            
            if mat_count == 0:
                print(f"  [INFO] No materials found")
                stats["files_processed"] += 1
                continue
            
            print(f"  [INFO] Found {mat_count} material(s)")
            
            # Import each material
            for mat in materials:
                mat_name = mat.GetName()
                try:
                    # Clone the material with all its data including textures
                    cloned_mat = mat.GetClone(c4d.COPYFLAGS_NONE)
                    
                    if not cloned_mat:
                        print(f"    ✗ {mat_name} - Clone failed")
                        stats["errors"] += 1
                        continue
                    
                    # Insert into active document
                    doc.InsertMaterial(cloned_mat)
                    stats["materials_imported"] += 1
                    imported_materials.append(f"{mat_name} (from: {filename})")
                    print(f"    ✓ {mat_name}")
                    
                except Exception as e:
                    print(f"    ✗ {mat_name} - {e}")
                    stats["errors"] += 1
            
            stats["files_processed"] += 1
            
        finally:
            # Clean up the source document
            if source_doc:
                c4d.documents.KillDocument(source_doc)
    
    # Update the scene
    c4d.EventAdd()
    
    # Write log file
    try:
        with open(log_path, 'w', encoding='utf-8') as log_file:
            log_file.write("=" * 60 + "\n")
            log_file.write("       C4D CENTER MATERIAL IMPORT LOG\n")
            log_file.write("=" * 60 + "\n")
            log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Source: {PARENT_DIRECTORY}\n")
            log_file.write(f"Target Scene: {doc.GetDocumentName()}\n")
            log_file.write("=" * 60 + "\n\n")
            log_file.write(f"Files Processed: {stats['files_processed']}\n")
            log_file.write(f"Materials Imported: {stats['materials_imported']}\n")
            log_file.write(f"Errors: {stats['errors']}\n\n")
            log_file.write("-" * 60 + "\n")
            log_file.write("IMPORTED MATERIALS:\n")
            log_file.write("-" * 60 + "\n")
            for mat_entry in imported_materials:
                log_file.write(f"  • {mat_entry}\n")
            log_file.write("\n" + "=" * 60 + "\n")
        print(f"\n[LOG] Import log saved to: {log_path}")
    except Exception as e:
        print(f"\n[WARNING] Could not write log file: {e}")
    
    print("\n" + "="*60)
    print("              IMPORT SUMMARY")
    print("="*60)
    print(f"  Files Processed:       {stats['files_processed']}")
    print(f"  Materials Imported:    {stats['materials_imported']}")
    print(f"  Errors:                {stats['errors']}")
    print("="*60)
    print("\n[SUCCESS] Materials have been imported to your current scene!")
    print("[INFO] Check the Material Manager to see all imported materials.")


if __name__ == '__main__':
    import_materials_to_scene()