from pathlib import Path

# Root structure
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"

RARITY_LIST = ["common", "uncommon", "rare", "rare+", "legendary", "legendary+", "mythical"]

def build_rarity_tag_map(tag_file_path):
    tag_map = {}
    if tag_file_path.exists():
        for line in tag_file_path.read_text(encoding="utf-8").splitlines():
            url = line.strip()
            if not url:
                continue
            for rarity in RARITY_LIST:
                if rarity.replace("+", "-1") in url:
                    tag_map[url] = rarity
                    break
    return tag_map

def load_links(file_path):
    if not file_path.exists():
        return []
    return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

def save_links(file_path, links):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("\n".join(links), encoding="utf-8")

def save_to_rarity(base_path, link, rarity):
    rarity_file = base_path / rarity / "_links.txt"
    existing = set(load_links(rarity_file))
    if link not in existing:
        existing.add(link)
        save_links(rarity_file, sorted(existing))

def process_thing_folder(thing_folder):
    name = thing_folder.name
    tag_file = thing_folder / f"{name}_tags.txt"
    untagged_file = thing_folder / "untagged" / "_links.txt"

    untagged_links = load_links(untagged_file)
    tag_map = build_rarity_tag_map(tag_file)

    if not untagged_links:
        return None

    print(f"\n📦 {name.upper()}: {len(untagged_links)} untagged links found.")
    print(f"🔖 {len(tag_map)} known tag links mapped to rarities.")

    return {
        "thing": name,
        "base_path": thing_folder,
        "untagged_file": untagged_file,
        "untagged_links": untagged_links,
        "tag_map": tag_map
    }

def prepare_all_things():
    all_things = []
    for thing_path in DATA_DIR.iterdir():
        if thing_path.is_dir():
            result = process_thing_folder(thing_path)
            if result:
                all_things.append(result)
    return all_things

if __name__ == "__main__":
    summary = prepare_all_things()
    print(f"\n✨ Ready to scrape tags for {len(summary)} groups.")
