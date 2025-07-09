from pathlib import Path

RARITY_FOLDERS = ["common", "uncommon", "rare", "rare+", "legendary", "legendary+", "mythical"]
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_links(path):
    if not path.exists():
        return set()
    return set(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def compare_links(thing_name):
    base = DATA_DIR / thing_name
    masterlist_path = base / "masterlist.txt"

    master_links = load_links(masterlist_path)
    tagged_links = set()

    for rarity in RARITY_FOLDERS:
        rarity_file = base / rarity / "_links.txt"
        tagged_links.update(load_links(rarity_file))

    untagged = sorted(master_links - tagged_links)

    print(f"\n📦 {thing_name.upper()} - Missing tags for {len(untagged)} links")
    for link in untagged:
        print(f"  ❌ {link}")

    # Optional: write to file
    if untagged:
        out_path = base / "untagged" / "_links.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(untagged), encoding="utf-8")
        print(f"💾 Saved to {out_path}")


def run_all():
    for thing_folder in DATA_DIR.iterdir():
        if thing_folder.is_dir():
            compare_links(thing_folder.name)


if __name__ == "__main__":
    run_all()
