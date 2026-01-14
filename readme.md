# C4D Center Material Scraper (v2.1)

A high-performance, fully interactive automation tool designed for the systematic extraction of 3D materials from the C4D Center library. This version features a complete CLI-based configuration wizard, removing the need for manual code edits.

<font color="red">-----UPDATE YOUR OWN RANDOMIZED INTERVAL TO MIMIC HUMAN-NESS. SUGGESTED IS 3-7 SECONDS -----</font>

> [!WARNING]
> UPDATE YOUR OWN RANDOMIZED INTERVAL TO MIMIC HUMAN-NESS. SUGGESTED IS 3-7 SECONDS. Running at high speeds may result in IP rate-limiting or server-side blocks.

---

## 🚀 Key Features

* **Interactive CLI Wizard:** On startup, the script prompts for download paths, headless preferences, and specific page ranges to ensure a user-friendly experience.
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
* **Clean Session Logging:** Generates a timestamped `.txt` log inside your chosen download folder for every successful session.

---

## 🛠 Prerequisites

* **Python:** 3.8+
* **Browser:** [Google Chrome](https://www.google.com/chrome/)
* **Drivers:** Managed automatically via `webdriver-manager`.

### Installation
```bash
pip install selenium webdriver-manager