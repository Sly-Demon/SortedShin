import re
from bs4 import BeautifulSoup
from pathlib import Path

# -------- CONFIG -------- #
SCRIPT_DIR = Path(__file__).resolve().parent
TEST_FILE = SCRIPT_DIR / "html" / "corpo-crystal.html"
# ------------------------ #

def extract_flexible_labeled_value(soup, label):
    print(f"\n🔎 Searching for label: {label}")

    label_span = soup.find("span", string=lambda t: t and t.strip() == label)
    if label_span:
        print(f"  Label span: {label_span}")
        current = label_span
        for _ in range(5):
            current = current.find_next()
            if not current:
                break
            if current.name == "span":
                strong = current.find("strong")
                if strong:
                    inner = strong.find("span")
                    if inner:
                        print(f"  ✅ Found nested span in strong: {inner.text.strip()}")
                        return inner.text.strip()
                if current.text and current.text.strip():
                    print(f"  ✅ Found direct span: {current.text.strip()}")
                    return current.text.strip()

    inline_span = soup.find("span", string=lambda t: t and t.strip().startswith(label))
    if inline_span:
        print(f"  Inline span: {inline_span}")
        return inline_span.text.strip().replace(label, "").strip(" :.")

    print("  ❌ No match found")
    return None

def parse_meta_mineral(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Meta name
        title_tag = soup.find("meta", property="og:title")
        name = title_tag["content"].strip() if title_tag else "Unknown"

        # Description fallback from meta
        desc_tag = soup.find("meta", property="og:description")
        desc_block = desc_tag["content"] if desc_tag else ""
        print(f"\n📝 Description meta: {desc_block[:100]}...")

        color = extract_flexible_labeled_value(soup, "Color:")
        location = extract_flexible_labeled_value(soup, "Mineral location:")
        rarity = extract_flexible_labeled_value(soup, "Mineral Rarity:")
        hardness = extract_flexible_labeled_value(soup, "Moh's Hardness Ranking:")
        melting_point = extract_flexible_labeled_value(soup, "Melting Point:")
        solubility = extract_flexible_labeled_value(soup, "Solubility:")
        market_value = extract_flexible_labeled_value(soup, "Market Value:")
        description = extract_flexible_labeled_value(soup, "Description:")
        if not description and "Description:" in desc_block:
            description = desc_block.split("Description:", 1)[-1].strip()

        return {
            "name": name,
            "color": color,
            "location": location,
            "rarity": rarity,
            "hardness": hardness,
            "melting_point": melting_point,
            "solubility": solubility,
            "market_value": market_value,
            "description": description
        }

    except Exception as e:
        print(f"\U0001F4A5 Failed to parse {file_path}: {e}")
        return None

if __name__ == "__main__":
    result = parse_meta_mineral(TEST_FILE)
    if result:
        print("\n💎 Parsed Mineral Meta Info:")
        for k, v in result.items():
            print(f"  {k.title().replace('_', ' ')}: {v}")
