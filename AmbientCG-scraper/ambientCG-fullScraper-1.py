import time
import os
import random
import sys
import ctypes
import json
import keyboard 
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. COLOR & LOGGING ENGINE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG_FILE = os.path.join(BASE_DIR, "scraper_debug.log")

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def trace(msg):
    t = datetime.now().strftime("%H:%M:%S")
    with open(DEBUG_FILE, "a") as f:
        f.write(f"[{t}] {msg}\n")
    print(f"{Color.CYAN}[{t}] [DEBUG]{Color.END} {msg}")

def status_log(asset_id, info=""):
    print(f"\n{Color.BOLD}{Color.YELLOW}>>> PROCESSING ASSET: {asset_id}{Color.END}")
    if info:
        print(f"    {Color.GREEN}Status: {info}{Color.END}")

# --- NEW FAILURE LOGGER ---
def log_failure(download_dir, asset_id, file_name, reason):
    md_file = os.path.join(download_dir, "failed_downloads.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create header if new file
    if not os.path.exists(md_file):
        with open(md_file, "w") as f:
            f.write("| Timestamp | Asset ID | File Name | Error Reason |\n")
            f.write("| --- | --- | --- | --- |\n")
    
    with open(md_file, "a") as f:
        f.write(f"| {timestamp} | **{asset_id}** | {file_name} | {reason} |\n")

with open(DEBUG_FILE, "w") as f:
    f.write(f"--- FULL AUTONOMOUS SESSION START: {datetime.now()} ---\n")

def ensure_popup_and_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        trace("Elevation required. Relaunching as Admin...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    return True

# --- 2. GLOBAL CONFIG ---
STOP_HOTKEY = 'ctrl+alt+shift+end' 
CONCURRENT_LIMIT = 8 
STAGGER_DELAY = (1.5, 3.5) 
stop_requested = False
stats = {"success": 0, "failed": 0}

def trigger_stop():
    global stop_requested
    trace("!!! EMERGENCY STOP DETECTED !!!")
    stop_requested = True

def get_active_downloads(download_path):
    files = [f for f in os.listdir(download_path) if f.endswith('.crdownload')]
    trace(f"Capacity Check: {len(files)}/{CONCURRENT_LIMIT} slots active.")
    return len(files)

CONFIG_FILE = os.path.join(BASE_DIR, "scraper_config_full.json")
QUEUE_FILE = os.path.join(BASE_DIR, "pending_assets.json")

def load_json(p): return json.load(open(p, "r")) if os.path.exists(p) else {}
def save_json(p, d): json.dump(d, open(p, "w"))

# --- 3. ENGINE ---
def run_scraper():
    global stop_requested
    keyboard.add_hotkey(STOP_HOTKEY, trigger_stop)

    try:
        config = load_json(CONFIG_FILE)
        download_dir = config.get("download_path")
        if not download_dir or not os.path.exists(download_dir):
            download_dir = input("Enter download path: ").strip().replace('"', '')
            save_json(CONFIG_FILE, {"download_path": download_dir})

        load_images = input("Enable image loading? (y/n): ").lower() in ['y', 'yes']
        block_ads = input("Disable ads? (y/n): ").lower() in ['y', 'yes']

        trace("Waking Chrome Driver...")
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.managed_default_content_settings.images": 1 if load_images else 2
        })
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        if block_ads:
            trace("Applying Network Filters...")
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*google-analytics.com*", "*doubleclick.net*", "*carbonads.net*"]})

        history_file = os.path.join(download_dir, "download_history.txt")
        processed = set()
        if os.path.exists(history_file):
            with open(history_file, "r") as f: processed = set(line.strip() for line in f if line.strip())

        # --- DYNAMIC INDEXING ---
        queue = load_json(QUEUE_FILE).get("pending", [])
        if not queue:
            # UPDATED URL to generic "Popular" list
            trace("Queue empty. Indexing master list (All Types)...")
            driver.get("https://ambientcg.com/list?sort=popular")
            time.sleep(5)
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while not stop_requested:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    trace("Reached end of visual list.")
                    break
                last_height = new_height
                trace("Scrolling for more assets...")

            blocks = driver.find_elements(By.CLASS_NAME, "asset-block")
            ids = [el.get_attribute("id").replace("asset-", "") for el in blocks if el.get_attribute("id")]
            queue = [aid for aid in ids if aid not in processed]
            save_json(QUEUE_FILE, {"pending": queue})
            trace(f"Indexing Complete. {len(queue)} assets added to queue.")

        # --- MAIN LOOP ---
        while queue and not stop_requested:
            active = get_active_downloads(download_dir)
            if active >= CONCURRENT_LIMIT:
                trace(f"At capacity ({active}). Waiting 4s...")
                time.sleep(4)
                continue

            asset_id = queue.pop(0)
            status_log(asset_id, "Scanning file types...")
            
            try:
                driver.get(f"https://ambientcg.com/view?id={asset_id}")
                time.sleep(1.5)
                
                # UPDATED SELECTOR: Targets ALL download buttons
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'get?file=')]")
                
                if not links:
                    trace(f"No download links found for {asset_id}.")
                    log_failure(download_dir, asset_id, "ALL", "No links found on page")
                    stats["failed"] += 1
                    continue

                clicked_count = 0
                for link in links:
                    label = link.text.strip().replace('\n', ' ')
                    
                    # LOGIC: Exclude JPG, allow everything else
                    if "JPG" in label.upper():
                        trace(f"Skipping excluded format: {label}")
                        continue
                    
                    try:
                        trace(f"Requesting: {label}")
                        driver.execute_script("arguments[0].click();", link)
                        clicked_count += 1
                        time.sleep(1.2)
                    except Exception as click_err:
                        trace(f"Failed to click {label}: {click_err}")
                        log_failure(download_dir, asset_id, label, str(click_err))

                if clicked_count > 0:
                    with open(history_file, "a") as hf: hf.write(f"{asset_id}\n")
                    stats["success"] += 1
                else:
                    trace(f"Asset {asset_id} had links but none matched criteria (likely all JPG).")
                
                save_json(QUEUE_FILE, {"pending": queue})
                time.sleep(random.uniform(*STAGGER_DELAY))

            except Exception as e:
                trace(f"CRITICAL ERROR on {asset_id}: {str(e)}")
                log_failure(download_dir, asset_id, "CRITICAL", str(e))
                stats["failed"] += 1
                save_json(QUEUE_FILE, {"pending": queue})

        while get_active_downloads(download_dir) > 0:
            trace("Waiting for final file transfers to finalize...")
            time.sleep(5)

    finally:
        trace(f"FULL SESSION COMPLETE. Success: {stats['success']} | Failed: {stats['failed']}")
        keyboard.unhook_all()
        try: driver.quit()
        except: pass
        input("\nAutonomous Session Ended. Press Enter to close.")

if __name__ == "__main__":
    if ensure_popup_and_admin():
        os.system("") 
        run_scraper()