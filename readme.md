# C4D Center Material Scraper (v2.1)

A high-performance, fully interactive automation tool designed for the systematic extraction of 3D materials from the C4D Center library. This version features a complete CLI-based configuration wizard, removing the need for manual code edits.

---

## 🚀 Key Features

* **Interactive CLI Wizard:** On startup, the script prompts for download paths, headless preferences, and specific page ranges to ensure a user-friendly experience.
* **Performance Optimization:** * **Eager Load Strategy:** Interacts with the DOM as soon as the basic structure is ready, rather than waiting for external trackers or ads.
    * **Image Suppression:** Disables image rendering to drastically reduce bandwidth and CPU usage during the crawl.
* **Stealth & Ethics:**
    * **Human-Mimicry Delays:** Uses randomized sub-2-second intervals (0.5s – 1.9s) to respect server load and avoid robotic request patterns.

-----UPDATE YOUR OWN RANDOMIZED INTERVAL TO MIMIC HUMAN-NESS. SUGGESTED IS 3-7 SECONDS -----

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