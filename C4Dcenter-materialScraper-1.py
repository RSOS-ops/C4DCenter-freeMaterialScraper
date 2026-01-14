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
    choice = choice.lower()
    if choice in ['y', 'yes']: return True, True, None
    if choice in ['n', 'no']: return True, False, None
    return False, None, "Please enter 'y' or 'n'."

def validate_int(val):
    try:
        ival = int(val)
        if ival < 1: return False, None, "Page number must be 1 or higher."
        return True, ival, None
    except ValueError:
        return False, None, "Please enter a valid number."

# Collect all configurations from user
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

# Randomized Delay Settings (Fast human mimicry)
MIN_DELAY = 0.5
MAX_DELAY = 1.9

# --- 2. BROWSER CONFIGURATION ---
chrome_options = Options()

if HEADLESS_MODE:
    chrome_options.add_argument("--headless=new")
    print("\n[Status] Initializing Headless Browser...")
else:
    print("\n[Status] Initializing GUI Browser...")

# Speed Optimization: Disable images
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "profile.managed_default_content_settings.images": 2 
})

# Speed Optimization: Eager page load strategy
chrome_options.page_load_strategy = 'eager'

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

downloaded_filenames = []

def wait_for_download_robust(directory, timeout=120):
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
            time.sleep(2) # Final safety buffer
            return True
    return False

# --- 3. MAIN LOOP ---
try:
    for page_num in range(START_PAGE, END_PAGE + 1):
        current_library_url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
        print(f"\n--- Page {page_num} of {END_PAGE} ---")
        driver.get(current_library_url)
        
        all_links = driver.find_elements(By.CSS_SELECTOR, "ul.products li.product a.woocommerce-LoopProduct-link")
        urls = list(dict.fromkeys([l.get_attribute("href") for l in all_links])) 

        for url in urls:
            material_slug = url.strip("/").split("/")[-1]
            if any(material_slug in f.lower() for f in os.listdir(DOWNLOAD_DIR)):
                print(f"Skipping: {material_slug}")
                continue

            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            files_before = set(os.listdir(DOWNLOAD_DIR))
            driver.get(url)
            
            try:
                btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "somdn-form-submit-button")))
                time.sleep(random.uniform(0.3, 0.6))
                driver.execute_script("arguments[0].click();", btn)
                
                if wait_for_download_robust(DOWNLOAD_DIR):
                    files_after = set(os.listdir(DOWNLOAD_DIR))
                    new_files = list(files_after - files_before)
                    actual_files = [f for f in new_files if not f.endswith(('.tmp', '.crdownload'))]
                    
                    if actual_files:
                        print(f"Success: {actual_files[0]} saved.")
                        if ENABLE_LOGGING: downloaded_filenames.append(actual_files[0])
            
            except Exception as e:
                print(f"Skipped: {material_slug} | Error: {str(e)[:40]}...")

finally:
    if ENABLE_LOGGING and downloaded_filenames:
        log_name = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(DOWNLOAD_DIR, log_name), "w") as f:
            f.write("\n".join(downloaded_filenames))
    driver.quit()