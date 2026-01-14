import time
import os
import random
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. INTERACTIVE SETUP ---

def get_input(prompt, validation_func):
    """Generic helper to handle user input and validation."""
    while True:
        value = input(prompt).strip()
        success, result, error_msg = validation_func(value)
        if success:
            return result
        print(f"Error: {error_msg}")

def validate_path(path):
    """Sanitizes and validates the download directory."""
    path = path.replace('"', '').replace("'", "")
    if not path: return False, None, "Path cannot be empty."
    if not os.path.exists(path):
        create = input(f"Directory '{path}' does not exist. Create it? (y/n): ").lower()
        if create == 'y':
            try:
                os.makedirs(path)
                return True, path, None
            except Exception as e:
                return False, None, str(e)
        return False, None, "Please provide an existing directory."
    return True, path, None

def validate_bool(choice):
    """Validates yes/no inputs for headless mode."""
    choice = choice.lower()
    if choice in ['y', 'yes']: return True, True, None
    if choice in ['n', 'no']: return True, False, None
    return False, None, "Please enter 'y' or 'n'."

def validate_int(val):
    """Validates page number inputs."""
    try:
        ival = int(val)
        if ival < 1: return False, None, "Page number must be 1 or higher."
        return True, ival, None
    except ValueError:
        return False, None, "Please enter a valid number."

# Collect session-specific configurations
print("--- C4D Center Scraper Configuration ---")
DOWNLOAD_DIR = get_input("1. Enter full download path: ", validate_path)
HEADLESS_MODE = get_input("2. Run in Headless Mode? (y/n): ", validate_bool)
START_PAGE = get_input("3. Enter Start Page: ", validate_int)
END_PAGE = get_input("4. Enter End Page: ", validate_int)

if START_PAGE > END_PAGE:
    print("\nWarning: Start page is greater than end page. Swapping them.")
    START_PAGE, END_PAGE = END_PAGE, START_PAGE

ENABLE_LOGGING = True  
BASE_URL = "https://c4dcenter.com/material-library/"

# Randomized Delay Settings (Mimics human browsing patterns)
# UPDATE YOUR OWN RANDOMIZED INTERVAL TO MIMIC HUMAN-NESS. SUGGESTED IS 3-7 SECONDS
MIN_DELAY = 0.5
MAX_DELAY = 1.9

# Statistics for Summary Report
stats = {
    "total_found": 0,
    "downloaded": 0,
    "skipped": 0,
    "errors": 0
}

# --- 2. BROWSER CONFIGURATION ---
chrome_options = Options()

if HEADLESS_MODE:
    chrome_options.add_argument("--headless=new")
    # Added: Standard window size prevents layout breaking in headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    print("\n[Status] Initializing Headless Browser...")
else:
    print("\n[Status] Initializing GUI Browser...")

# Speed Optimization: Disable images to save bandwidth
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "profile.managed_default_content_settings.images": 2 
})

# Speed Optimization: Eager page load strategy (DOM ready)
chrome_options.page_load_strategy = 'eager'

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

downloaded_filenames = []

def wait_for_download_robust(directory, timeout=120):
    """Waits for download completion by watching for Chrome temp files."""
    start_time = time.time()
    while time.time() - start_time < 15: 
        if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in os.listdir(directory)):
            break
        time.sleep(0.5)

    seconds = 0
    while seconds < timeout:
        files = os.listdir(directory)
        if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in files):
            time.sleep(1)
            seconds += 1
        else:
            time.sleep(2) # Mandatory 2-second buffer for file renaming
            return True
    return False

# --- 3. MAIN LOOP ---
try:
    for page_num in range(START_PAGE, END_PAGE + 1):
        current_library_url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
        print(f"\n--- Page {page_num} of {END_PAGE} ---")
        
        driver.get(current_library_url)
        
        # Stability pause: Allows headless engine to settle after navigation
        time.sleep(1)

        try:
            # Explicitly wait for the product list before processing links
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.products")))
            
            all_links = driver.find_elements(By.CSS_SELECTOR, "ul.products li.product a.woocommerce-LoopProduct-link")
            urls = list(dict.fromkeys([l.get_attribute("href") for l in all_links])) 
            stats["total_found"] += len(urls)

            for url in urls:
                material_slug = url.strip("/").split("/")[-1]
                
                # Check for existing files
                if any(material_slug in f.lower() for f in os.listdir(DOWNLOAD_DIR)):
                    print(f"Skipping: {material_slug} (Already exists)")
                    stats["skipped"] += 1
                    continue

                # NEW: Print current target material
                print(f"Starting download: {material_slug}...")

                # Human-mimicry delay
                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                
                files_before = set(os.listdir(DOWNLOAD_DIR))
                driver.get(url)
                
                try:
                    # Wait for download button to be interactable
                    btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "somdn-form-submit-button")))
                    
                    # Micro-jitter before action
                    time.sleep(random.uniform(0.3, 0.6))
                    driver.execute_script("arguments[0].click();", btn)
                    
                    if wait_for_download_robust(DOWNLOAD_DIR):
                        files_after = set(os.listdir(DOWNLOAD_DIR))
                        new_files = list(files_after - files_before)
                        actual_files = [f for f in new_files if not f.endswith(('.tmp', '.crdownload'))]
                        
                        if actual_files:
                            print(f"Success: {actual_files[0]} saved.")
                            stats["downloaded"] += 1
                            if ENABLE_LOGGING: downloaded_filenames.append(actual_files[0])
                
                except Exception as e:
                    print(f"Skipped: {material_slug} | Error: {str(e)[:40]}...")
                    stats["errors"] += 1

        except Exception as page_error:
            print(f"Critical error on library page {page_num}: {str(page_error)[:50]}")

finally:
    # 1. Final Summary Report
    print("\n" + "="*40)
    print("           SESSION SUMMARY")
    print("="*40)
    print(f"Total Materials Found:  {stats['total_found']}")
    print(f"Successful Downloads:   {stats['downloaded']}")
    print(f"Skipped (Duplicates):   {stats['skipped']}")
    print(f"Errors Encountered:     {stats['errors']}")
    print("="*40)

    # 2. Finalize log generation inside the target download folder
    if ENABLE_LOGGING and downloaded_filenames:
        log_name = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(DOWNLOAD_DIR, log_name), "w") as f:
            f.write("\n".join(downloaded_filenames))
        print(f"Log saved to: {log_name}")
    
    driver.quit()