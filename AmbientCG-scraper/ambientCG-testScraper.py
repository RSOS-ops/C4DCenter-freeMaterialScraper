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

# --- 1. COLOR & RUNNING LOG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_LOG = os.path.join(BASE_DIR, "test_debug.log")

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def trace(msg):
    t = datetime.now().strftime("%H:%M:%S")
    with open(TEST_LOG, "a") as f:
        f.write(f"[{t}] {msg}\n")
    print(f"{Color.CYAN}[{t}] [DEBUG]{Color.END} {msg}")

def status_log(asset_id, count, total):
    print(f"\n{Color.BOLD}{Color.YELLOW}--- TEST ASSET {count}/{total}: {asset_id} ---{Color.END}")

with open(TEST_LOG, "w") as f:
    f.write(f"--- TEST SESSION START: {datetime.now()} ---\n")

def ensure_popup_and_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    return True

# --- 2. SETTINGS ---
TEST_ITEM_LIMIT = 25 
CONCURRENT_LIMIT = 8 
STAGGER_DELAY = (1.5, 3.5)
STOP_HOTKEY = 'ctrl+alt+shift+end' 
stop_requested = False
stats = {"success": 0, "failed": 0}

def trigger_stop():
    global stop_requested
    trace("STOP REQUESTED.")
    stop_requested = True

def get_active_downloads(path):
    files = [f for f in os.listdir(path) if f.endswith('.crdownload')]
    trace(f"Checking Slots: {len(files)} active.")
    return len(files)

CONFIG_FILE = os.path.join(BASE_DIR, "scraper_config_test.json")
QUEUE_FILE = os.path.join(BASE_DIR, "pending_assets_test.json")

def load_json(p): return json.load(open(p, "r")) if os.path.exists(p) else {}
def save_json(p, d): json.dump(d, open(p, "w"))

def run_test_scraper():
    global stop_requested
    session_count = 0
    keyboard.add_hotkey(STOP_HOTKEY, trigger_stop)

    try:
        config = load_json(CONFIG_FILE)
        download_dir = config.get("download_path")
        if not download_dir:
            download_dir = input("Enter download path: ").strip().replace('"', '')
            save_json(CONFIG_FILE, {"download_path": download_dir})

        load_images = input("Enable images? (y/n): ").lower() in ['y', 'yes']
        block_ads = input("Block ads? (y/n): ").lower() in ['y', 'yes']

        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.managed_default_content_settings.images": 1 if load_images else 2
        })
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        if block_ads:
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*google-analytics.com*", "*doubleclick.net*", "*carbonads.net*"]})

        history_file = os.path.join(download_dir, "download_history.txt")
        processed = set()
        if os.path.exists(history_file):
            with open(history_file, "r") as f: processed = set(line.strip() for line in f if line.strip())

        queue = load_json(QUEUE_FILE).get("pending", [])
        if not queue:
            trace("Indexing assets for test...")
            driver.get("https://ambientcg.com/list?type=material%2Cdecal%2Catlas&sort=popular")
            time.sleep(5)
            blocks = driver.find_elements(By.CLASS_NAME, "asset-block")
            ids = [el.get_attribute("id").replace("asset-", "") for el in blocks if el.get_attribute("id")]
            queue = [aid for aid in ids if aid not in processed][:TEST_ITEM_LIMIT]
            save_json(QUEUE_FILE, {"pending": queue})

        while queue and not stop_requested and session_count < TEST_ITEM_LIMIT:
            active = get_active_downloads(download_dir)
            if active >= CONCURRENT_LIMIT:
                trace(f"Slots full ({active}). Waiting 4s...")
                time.sleep(4)
                continue

            asset_id = queue.pop(0)
            status_log(asset_id, session_count+1, TEST_ITEM_LIMIT)
            
            try:
                driver.get(f"https://ambientcg.com/view?id={asset_id}")
                time.sleep(1.5)
                links = driver.find_elements(By.XPATH, "//a[contains(., 'PNG')]")
                
                for link in links:
                    label = link.text.strip().replace('\n', ' ')
                    trace(f"Triggering {label}")
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(1)
                
                with open(history_file, "a") as hf: hf.write(f"{asset_id}\n")
                save_json(QUEUE_FILE, {"pending": queue})
                session_count += 1
                stats["success"] += 1
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                trace(f"FAILED on {asset_id}: {str(e)}")
                stats["failed"] += 1
                save_json(QUEUE_FILE, {"pending": queue})

        while get_active_downloads(download_dir) > 0:
            time.sleep(2)

    finally:
        keyboard.unhook_all()
        try: driver.quit()
        except: pass
        input("\nTest Complete. Press Enter.")

if __name__ == "__main__":
    if ensure_popup_and_admin():
        os.system("") 
        run_test_scraper()