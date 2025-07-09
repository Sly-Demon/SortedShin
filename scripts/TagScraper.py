import time
from datetime import datetime
from scraper_utils import chunk_links, get_selenium_driver, extract_tags_from_page
from TagExtractor import prepare_all_things, save_to_rarity, save_links

def clean_url(url):
    return url.strip().replace(" ", "").lower()

def match_tag_to_rarity(tag, known_tags):
    for tag_url, rarity in known_tags.items():
        if tag.replace("+", "-1") in tag_url:
            return rarity
    return None

def process_links_for_thing(thing_info):
    name = thing_info["thing"]
    print(f"\n🔍 Processing {name.upper()} links...")

    all_links = thing_info["untagged_links"]
    tag_map = thing_info["tag_map"]
    untagged_path = thing_info["untagged_file"]
    base_path = thing_info["base_path"]

    failed = []
    kept = []

    chunks = chunk_links(all_links)
    driver = get_selenium_driver()

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

                found_rarity = None
                for tag in tags:
                    rarity = match_tag_to_rarity(tag, tag_map)
                    if rarity:
                        found_rarity = rarity
                        break

                if found_rarity:
                    print(f"    ✅ Tag matched: {found_rarity}")
                    save_to_rarity(base_path, link, found_rarity)
                else:
                    print(f"    ❌ No matching rarity tag.")
                    failed.append(link)
                    kept.append(link)
            except Exception as e:
                print(f"    💥 Error: {e}")
                failed.append(link)
                kept.append(link)

    driver.quit()

    # Overwrite untagged with only kept
    save_links(untagged_path, kept)

    # Log failures
    if failed:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fail_file = base_path / f"failed_links_{name}_{ts}.txt"
        save_links(fail_file, failed)
        print(f"\n⚠️ Logged {len(failed)} failed links to {fail_file.name}")
    else:
        print(f"\n🎉 No failed links for {name}!")

def run_all_tag_scraping():
    targets = prepare_all_things()
    for thing in targets:
        process_links_for_thing(thing)

if __name__ == "__main__":
    run_all_tag_scraping()
