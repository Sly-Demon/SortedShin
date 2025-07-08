from pathlib import Path

# Set root relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"

RARITY_LIST = ["common", "uncommon", "rare", "rare_plus", "legendary", "legendary_plus", "mythical"]

def read_links(file_path):
    if not file_path.exists():
        return []
    return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

def write_links(file_path, links):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("\n".join(links), encoding="utf-8")

def prompt_yes_no(prompt):
    while True:
        choice = input(prompt + " (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"

def prompt_rarity():
    while True:
        rarity = input(f"🧠 Enter rarity ({', '.join(RARITY_LIST)}): ").strip().lower()
        if rarity in RARITY_LIST:
            return rarity
        print("❌ Invalid rarity. Try again.")

def manual_tag_sorter():
    pending_review = []
    for thing_path in DATA_DIR.iterdir():
        if not thing_path.is_dir():
            continue

        thing = thing_path.name
        untagged_file = thing_path / "untagged" / "_links.txt"
        links = read_links(untagged_file)

        if not links:
            continue

        print(f"\n❓ {thing.upper()} has {len(links)} untagged links.")
        if not prompt_yes_no(f"Do you have tag data for {thing}?"):
            pending_review.append(thing)
            continue

        remaining = []
        for link in links:
            print(f"\n🔗 {link}")
            if prompt_yes_no("Do you know the rarity for this link?"):
                rarity = prompt_rarity()
                rarity_file = thing_path / rarity / "_links.txt"
                rarity_links = set(read_links(rarity_file))
                if link not in rarity_links:
                    rarity_links.add(link)
                    write_links(rarity_file, sorted(rarity_links))
                    print(f"✅ Moved to {rarity}/_links.txt")
                else:
                    print(f"⚠️ Link already exists in {rarity}/_links.txt")
            else:
                remaining.append(link)

        write_links(untagged_file, remaining)
        print(f"\n🧾 {thing.upper()} Results: {len(links) - len(remaining)} moved, {len(remaining)} remaining in untagged.")

    if pending_review:
        print("\n🕗 Things still pending manual review:")
        for thing in pending_review:
            print(f"  - {thing}")

if __name__ == "__main__":
    manual_tag_sorter()
