import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"

# ----------- CONFIG -----------
THING = "flora"
UNTAGGED_PATH = Path("data/flora/_links.txt").resolve()
RARITY_DIR = Path("data/flora/by_rarity")
RARITY_TAG_MAP = {
    "flora-availability-common": "common",
    "flora-availability-uncommon": "uncommon",
    "flora-availability-rare": "rare",
    "flora-availability-rare-1": "rare+",
    "flora-availability-legendary": "legendary",
    "flora-availability-legendary-1": "legendary+",
    "flora-availability-mythical": "mythical"
}
CHUNK_SIZE = 75
# --------------------------------

def chunk_links(links, size=CHUNK_SIZE):
    for i in range(0, len(links), size):
        yield links[i:i+size]

def get_selenium_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def extract_tags_from_page(driver):
    try:
        time.sleep(1)
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/world-book/tags/']")
        tags = [el.get_attribute("href").split("/")[-1].strip().lower() for el in elements]
        return tags
    except Exception as e:
        print(f"    ⚠️ Tag extract error: {e}")
        return []

def match_tag_to_rarity(tag):
    tag = tag.replace("+", "-1").lower()
    return RARITY_TAG_MAP.get(tag, None)

def save_to_rarity(link, rarity):
    rarity_file = RARITY_DIR / f"{rarity}.txt"
    rarity_file.parent.mkdir(parents=True, exist_ok=True)
    with rarity_file.open("a", encoding="utf-8") as f:
        f.write(link + "\n")

def save_links(path, links):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.writelines([l.strip() + "\n" for l in links])

def run_flora_tag_sorter():
    print(f"\n📦 {THING.upper()} Tag Sorter")

    print(f"🔎 Looking for untagged at: data/flora/untagged/_links.txt")
    UNTAGGED_PATH = DATA_DIR / "flora" / "untagged" / "_links.txt"


    all_links = [line.strip() for line in UNTAGGED_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not all_links:
        print("🚫 File exists but contains no links.")
        return

    print(f"✅ {len(all_links)} untagged links loaded.")

    failed = []
    kept = []

    driver = get_selenium_driver()
    chunks = list(chunk_links(all_links))

    for chunk_num, chunk in enumerate(chunks):
        print(f"\n📦 Chunk {chunk_num+1}/{len(chunks)} - {len(chunk)} links")
        for i, link in enumerate(chunk, 1):
            print(f"  → ({i}/{len(chunk)}) {link}")
            try:
                driver.get(link)
                tags = extract_tags_from_page(driver)

                if not tags:
                    print("    ⚠️ No tags found.")
                    failed.append(link)
                    kept.append(link)
                    continue

                found = False
                for tag in tags:
                    rarity = match_tag_to_rarity(tag)
                    if rarity:
                        print(f"    ✅ Tag matched: {rarity}")
                        save_to_rarity(link, rarity)
                        found = True
                        break

                if not found:
                    print(f"    ❌ No matching rarity tag.")
                    failed.append(link)
                    kept.append(link)

            except Exception as e:
                print(f"    💥 Error: {e}")
                failed.append(link)
                kept.append(link)

    driver.quit()

    # Save remaining untagged links
    save_links(UNTAGGED_PATH, kept)

    # Save failed links separately
    if failed:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fail_file = UNTAGGED_PATH.parent / f"failed_links_{THING}_{ts}.txt"
        save_links(fail_file, failed)
        print(f"\n⚠️ Logged {len(failed)} failed links to {fail_file.name}")
    else:
        print(f"\n🎉 No failed links!")

if __name__ == "__main__":
    run_flora_tag_sorter()
