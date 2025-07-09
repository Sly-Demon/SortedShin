import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# -------- CONFIG --------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "parsed"
MAX_THREADS = 6  # Adjust depending on your CPU/RAM

# -------- HELPERS --------
def normalize_filename(name):
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name.strip("_")

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)

def extract_info(html):
    soup = BeautifulSoup(html, "html.parser")
    name_el = soup.find("h1")
    desc_el = soup.find("div", class_="post-rich") or soup.find("div", class_="content")
    name = name_el.get_text(strip=True) if name_el else "unknown"
    desc = desc_el.get_text(strip=True) if desc_el else "no description"
    return name, desc

def scrape_and_save(link, thing):
    driver = get_driver()
    try:
        driver.get(link)
        time.sleep(1)  # Short adaptive wait
        name, desc = extract_info(driver.page_source)
        filename = normalize_filename(name) + ".txt"
        out_path = OUTPUT_DIR / thing / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            f.write(f"Name: {name}\nLink: {link}\n\nDescription:\n{desc}")
        print(f"  ✅ Saved: {filename}")
    except Exception as e:
        print(f"  💥 Failed to scrape {link}: {e}")
    finally:
        driver.quit()

# -------- MAIN --------
def get_all_links(thing):
    thing_dir = DATA_DIR / thing
    all_links = []
    for folder in thing_dir.glob("**/"):
        if "untagged" in folder.parts or not folder.is_dir():
            continue
        for txt in folder.glob("*_links.txt"):
            links = [l.strip() for l in txt.read_text(encoding="utf-8").splitlines() if l.strip()]
            all_links.extend((link, thing) for link in links)
    return all_links

def turbo_scrape(thing="flora"):
    print(f"\n🚀 Turbo Scraping All {thing.upper()} Links")
    all_links = get_all_links(thing)
    print(f"🔗 Total Links Found: {len(all_links)}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(scrape_and_save, link, thing) for link, thing in all_links]
        for i, _ in enumerate(as_completed(futures), 1):
            print(f"  [{i}/{len(futures)}] done")

    print(f"\n🎉 DONE! Output in: {OUTPUT_DIR / thing}")

# -------- RUN --------
if __name__ == "__main__":
    for thing_dir in DATA_DIR.iterdir():
        if thing_dir.is_dir() and not thing_dir.name.startswith("parsed"):
            turbo_scrape(thing_dir.name)
