import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

# ------------------- CONFIG ------------------- #
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
HTML_DIR = SCRIPT_DIR / "html"
OUTPUT_DIR = DATA_DIR / "parsed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DEBUG = True
# ---------------------------------------------- #

def debug(msg):
    if DEBUG:
        print(msg)

def load_masterlists():
    all_master = {}
    for thing in ["flora", "fauna", "minerals"]:
        master_path = DATA_DIR / thing / "masterlist.txt"
        debug(f"📂 Looking for masterlist: {master_path}")
        if master_path.exists():
            entries = [Path(url).stem.strip().lower() for url in master_path.read_text(encoding="utf-8").splitlines() if url.strip()]
            all_master[thing] = set(entries)
            debug(f"✅ Loaded {len(entries)} entries from {thing}/masterlist.txt")
        else:
            debug(f"⚠️ Masterlist for {thing} not found.")
            all_master[thing] = set()
    return all_master

def extract_flexible_labeled_value(soup, label):
    label_span = soup.find("span", string=lambda t: t and t.strip() == label)
    if label_span:
        outer = label_span.find_next_sibling("span")
        if outer:
            strong = outer.find("strong")
            if strong:
                inner_span = strong.find("span")
                if inner_span:
                    debug(f"  ✅ Found deep span: {inner_span.text.strip()}")
                    return inner_span.text.strip()
        debug("  ⛔ No strong/span combo found after label")
    inline = soup.find("span", string=lambda t: t and t.strip().startswith(label))
    if inline:
        value = inline.text.strip().replace(label, "").strip(" .:")
        debug(f"  ✅ Found inline span: {value}")
        return value
    return None

def parse_fauna(soup, desc_block):
    data = {
        "abilities": None,
        "rank": None,
        "rarity": None,
        "region": None,
        "description": None
    }

    abilities_match = re.search(r"Abilities:\s*(.*?)(?=Danger Ranking:|Rarity:|Region:|Description:|$)", desc_block, re.DOTALL)
    if abilities_match:
        data["abilities"] = abilities_match.group(1).strip().replace("\n", " ")
    rank_match = re.search(r"Danger Ranking:\s*([A-Z])", desc_block)
    if rank_match:
        data["rank"] = rank_match.group(1).strip()

    for label in ["Rarity:", "Region:", "Danger Ranking:", "Description:"]:
        debug(f"🔎 Searching for label: {label}")
        value = extract_flexible_labeled_value(soup, label)
        if label == "Rarity:":
            data["rarity"] = value
        elif label == "Region:":
            data["region"] = value
        elif label == "Danger Ranking:" and value:
            data["rank"] = value
        elif label == "Description:":
            data["description"] = value

    return data

def parse_flora(soup):
    data = {
        "availability": extract_flexible_labeled_value(soup, "Availability:"),
        "region": extract_flexible_labeled_value(soup, "Region:"),
        "preparation": extract_flexible_labeled_value(soup, "Preparation:"),
        "cost": extract_flexible_labeled_value(soup, "Cost:"),
        "description": extract_flexible_labeled_value(soup, "Description:")
    }
    return data

def parse_minerals(soup):
    data = {
        "color": extract_flexible_labeled_value(soup, "Color:"),
        "location": extract_flexible_labeled_value(soup, "Mineral location:"),
        "rarity": extract_flexible_labeled_value(soup, "Mineral Rarity:"),
        "hardness": extract_flexible_labeled_value(soup, "Moh's Hardness Ranking:"),
        "melting_point": extract_flexible_labeled_value(soup, "Melting Point:"),
        "solubility": extract_flexible_labeled_value(soup, "Solubility:"),
        "market_value": extract_flexible_labeled_value(soup, "Market Value:"),
        "description": extract_flexible_labeled_value(soup, "Description:")
    }
    return data

def parse_file(filepath, category):
    try:
        debug(f"\n📄 Parsing: {filepath.name}")
        soup = BeautifulSoup(filepath.read_text(encoding="utf-8"), "html.parser")
        name = soup.find("meta", property="og:title")["content"]
        desc_block = soup.find("meta", property="og:description")["content"]

        if category == "fauna":
            result = parse_fauna(soup, desc_block)
        elif category == "flora":
            result = parse_flora(soup)
        elif category == "minerals":
            result = parse_minerals(soup)
        else:
            return None

        result["name"] = name
        return result
    except Exception as e:
        print(f"❌ Failed to parse {filepath.name}: {e}")
        return None

def main():
    master = load_masterlists()
    all_results = {"flora": [], "fauna": [], "minerals": []}

    debug(f"\n🔍 Checking HTML directory: {HTML_DIR}")
    for file in HTML_DIR.glob("*.html"):
        base = file.stem.lower()
        matched_type = None
        for category, entries in master.items():
            if base in entries:
                matched_type = category
                break
        if not matched_type:
            debug(f"⚠️ Skipped (unmatched): {file.name}")
            continue

        result = parse_file(file, matched_type)
        if result:
            all_results[matched_type].append(result)

    for category, entries in all_results.items():
        if entries:
            out_path = OUTPUT_DIR / f"{category}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(entries)} {category} entries → {out_path}")
        else:
            print(f"⚠️ No parsed entries for: {category}")

if __name__ == "__main__":
    main()
