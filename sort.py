import os
import re

# === CONFIG ===
base_dir = os.path.join(".venv", "data", "flora")
untagged_file = os.path.join(base_dir, "untagged", "_links.txt")
rarities = [
    "common", "uncommon", "rare", "rare_plus",
    "legendary", "legendary_plus", "mythical"
]


def normalize(url):
    return url.strip().rstrip("/").lower()


def load_links_from_file(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        return set(normalize(line) for line in f if line.strip())


def write_links_to_file(file_path, links):
    with open(file_path, "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")


def run_crosscheck_sort(raw_lines):
    # Step 1: Parse the raw input
    input_links = set()
    entries = []

    for line in raw_lines.strip().splitlines():
        match = re.match(r"^\s*(.+?)\s*:\s*.+?\s*:\s*(https?://[^\s]+)", line)
        if match:
            raw_rarity, raw_url = match.group(1), match.group(2)
            rarity = raw_rarity.lower().replace(" ", "_")
            url = normalize(raw_url)
            if rarity in rarities:
                entries.append((rarity, url))
                input_links.add(url)

    print(f"🔍 Parsed {len(entries)} valid entries from input.")

    # Step 2: Load all sorted links
    sorted_links = set()
    rarity_map = {}
    for rarity in rarities:
        rarity_path = os.path.join(base_dir, rarity, "_links.txt")
        links = load_links_from_file(rarity_path)
        sorted_links.update(links)
        for link in links:
            rarity_map[link] = rarity

    # Step 3: Load untagged
    untagged_links = load_links_from_file(untagged_file)

    already_sorted = 0
    fixed = 0
    still_unsorted = 0
    newly_sorted_by_rarity = {r: [] for r in rarities}

    for rarity, url in entries:
        if url in sorted_links:
            already_sorted += 1
            continue

        if url in untagged_links:
            newly_sorted_by_rarity[rarity].append(url)
            fixed += 1
        else:
            still_unsorted += 1

    # Step 4: Write changes
    if fixed:
        # Remove fixed from untagged
        untagged_links -= {link for sublist in newly_sorted_by_rarity.values() for link in sublist}
        write_links_to_file(untagged_file, untagged_links)

        # Append to correct rarity files
        for rarity, new_links in newly_sorted_by_rarity.items():
            rarity_file = os.path.join(base_dir, rarity, "_links.txt")
            existing = load_links_from_file(rarity_file)
            combined = existing.union(set(new_links))
            write_links_to_file(rarity_file, combined)

    # Step 5: Print results
    print("\n📊 SUMMARY")
    print(f"✔️ Already sorted: {already_sorted}")
    print(f"📥 Sorted from untagged: {fixed}")
    print(f"❗ Still unsorted: {still_unsorted}")


# === RAW INPUT ===
raw_flora = """
Extremely rare : Aldaka : https://www.shinseina.world/post/aldaka
Extremely rare : Felmather : https://www.shinseina.world/post/felmather
Extremely rare : Purfic : https://www.shinseina.world/post/purfic
Legendary : Crystal Apple : https://www.shinseina.world/post/crystal-apple
Rare : Asarabacca : https://www.shinseina.world/post/asarabacca
Rare : Atamale : https://www.shinseina.world/post/atamale
Rare : Colorful Death : https://www.shinseina.world/post/colorful-death
Rare : Curmona : https://www.shinseina.world/post/curmona
Rare : Dragonwort : https://www.shinseina.world/post/dragonwort
Rare : Edram : https://www.shinseina.world/post/edram
Rare : Entriste : https://www.shinseina.world/post/entriste
Rare : Ex-Scrom : https://www.shinseina.world/post/ex-scrom
Rare : Eyetic : https://www.shinseina.world/post/eyetic
Rare : Fury Flower : https://www.shinseina.world/post/fury-flower
Rare : Golden Cherry : https://www.shinseina.world/post/golden-cherry
Rare : Man-Eater : https://www.shinseina.world/post/man-eater
Rare : Prota : https://www.shinseina.world/post/prota
Rare : Suaeysit : https://www.shinseina.world/post/suaeysit
Rare : White bryony : https://www.shinseina.world/post/white-bryony
Rare : White Death : https://www.shinseina.world/post/white-death
Rare : Wolfsbane : https://www.shinseina.world/post/wolfsbane
Uncommon : Agrimony : https://www.shinseina.world/post/agrimony
Uncommon : Angelica : https://www.shinseina.world/post/angelica
Uncommon : Balm : https://www.shinseina.world/post/_balm
Uncommon : Barberry : https://www.shinseina.world/post/barberry
Uncommon : Black Stinger : https://www.shinseina.world/post/black-stinger
Uncommon : Blood Lotus : https://www.shinseina.world/post/blood-lotus
Uncommon : Borage : https://www.shinseina.world/post/borage
Uncommon : Deadly nightshade : https://www.shinseina.world/post/deadly-nightshade
Uncommon : Devil's Berry : https://www.shinseina.world/post/devil-s-berry
Uncommon : False Bliss : https://www.shinseina.world/post/false-bliss
Uncommon : Falsifal : https://www.shinseina.world/post/falsifal
Uncommon : Flyhigh : https://www.shinseina.world/post/flyhigh
Uncommon : Joywhisper : https://www.shinseina.world/post/joywhisper
Uncommon : Nitebell Mushroom : https://www.shinseina.world/post/nitebell-mushroom
Uncommon : Oxshoom : https://www.shinseina.world/post/oxshoom
Uncommon : Pogo : https://www.shinseina.world/post/_pogo
Uncommon : Pollen Whisper : https://www.shinseina.world/post/pollen-whisper
Uncommon : Tamariske : https://www.shinseina.world/post/tamariske
Uncommon : Watire : https://www.shinseina.world/post/watire
Uncommon : Weeping Willow : https://www.shinseina.world/post/weeping-willow
Uncommon : Willow-Herb : https://www.shinseina.world/post/willow-herb
Uncommon : Zulsendra : https://www.shinseina.world/post/zulsendra
Uncommon : Zur : https://www.shinseina.world/post/__zur
Common : Aloe : https://www.shinseina.world/post/_aloe
Common : Ash : https://www.shinseina.world/post/__ash
Common : Cokecane : https://www.shinseina.world/post/cokecane
Common : Culkas : https://www.shinseina.world/post/culkas
Common : Fire Berry : https://www.shinseina.world/post/fire-berry
Common : Glow Plant : https://www.shinseina.world/post/glow-plant
Common : Lightsway : https://www.shinseina.world/post/lightsway
Common : Popono : https://www.shinseina.world/post/popono
Common : Seeee : https://www.shinseina.world/post/seeee
Common : Shepherd's Purse : https://www.shinseina.world/post/shepherd-s-purse
Common : Weed : https://www.shinseina.world/post/_weed
Common : Wetalu : https://www.shinseina.world/post/wetalu
Common : Yarrow : https://www.shinseina.world/post/yarrow
Common : Vervain : https://www.shinseina.world/post/vervain
"""

# === EXECUTE ===
if __name__ == "__main__":
    run_crosscheck_sort(raw_flora)
