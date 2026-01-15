import time
import os
import random
import sys
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION & CONFIG HELPERS ---

# UNIQUE CONFIG FILENAME FOR C4DCENTER
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "scraper_config_c4d.json")

def load_config():
    """Retrieves the saved download path from the local folder."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(download_path):
    """Saves the path so you don't have to enter it next time."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"download_path": download_path}, f)

def get_input(prompt, validation_func):
    while True:
        value = input(prompt).strip()
        success, result, error_msg = validation_func(value)
        if success: return result
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
        return False, None, "Invalid directory."
    return True, path, None

def validate_bool(choice):
    if choice.lower() in ['y', 'yes']: return True, True, None
    if choice.lower() in ['n', 'no']: return True, False, None
    return False, None, "Enter 'y' or 'n'."

def validate_int(val):
    try:
        ival = int(val)
        if ival < 1: return False, None, "Must be 1 or higher."
        return True, ival, None
    except ValueError: return False, None, "Enter a valid number."

# --- 2. BROWSER SETUP & LOGIC ---

def run_scraper():
    print("--- C4D Center Scraper (v1.1) ---")

    # Load or request download path
    config = load_config()
    saved_path = config.get("download_path")
    
    if saved_path and os.path.exists(saved_path):
        print(f"[INFO] Using remembered path: {saved_path}")
        DOWNLOAD_DIR = saved_path
    else:
        DOWNLOAD_DIR = get_input("1. Enter full download path: ", validate_path)
        save_config(DOWNLOAD_DIR)

    HEADLESS_MODE = get_input("2. Run in Headless Mode? (y/n): ", validate_bool)
    START_PAGE = get_input("3. Enter Start Page: ", validate_int)
    END_PAGE = get_input("4. Enter End Page: ", validate_int)

    # Statistics
    stats = {"total_found": 0, "downloaded": 0, "skipped": 0, "errors": 0}
    
    chrome_options = Options()
    if HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "profile.managed_default_content_settings.images": 2 
    })
    chrome_options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    downloaded_filenames = []

    try:
        for page_num in range(START_PAGE, END_PAGE + 1):
            url = "https://c4dcenter.com/material-library/" if page_num == 1 else f"https://c4dcenter.com/material-library/page/{page_num}/"
            print(f"\n--- Page {page_num} of {END_PAGE} ---")
            driver.get(url)
            
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.products")))
                all_links = driver.find_elements(By.CSS_SELECTOR, "ul.products li.product a.woocommerce-LoopProduct-link")
                urls = list(dict.fromkeys([l.get_attribute("href") for l in all_links]))
                stats["total_found"] += len(urls)

                for target_url in urls:
                    slug = target_url.strip("/").split("/")[-1]
                    
                    # Check for duplicates in folder
                    if any(slug in f.lower() for f in os.listdir(DOWNLOAD_DIR)):
                        print(f"Skipping: {slug} (Exists)")
                        stats["skipped"] += 1
                        continue

                    print(f"Downloading: {slug}...")
                    time.sleep(random.uniform(1.0, 2.5))
                    
                    driver.get(target_url)
                    try:
                        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "somdn-form-submit-button")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # Wait logic... (Simplified for brevity)
                        time.sleep(5) 
                        stats["downloaded"] += 1
                        downloaded_filenames.append(slug)
                    except:
                        stats["errors"] += 1
            except:
                print(f"Error loading page {page_num}")

    finally:
        # Final Log
        if downloaded_filenames:
            log_name = f"log_c4d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(os.path.join(DOWNLOAD_DIR, log_name), "w") as f:
                f.write("\n".join(downloaded_filenames))
            print(f"\nSession complete. Log saved to your download folder.")
        
        driver.quit()

if __name__ == "__main__":
    run_scraper()