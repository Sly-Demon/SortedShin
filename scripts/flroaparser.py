import re
from bs4 import BeautifulSoup
from pathlib import Path

# -------- CONFIG -------- #
SCRIPT_DIR = Path(__file__).resolve().parent
TEST_FILE = SCRIPT_DIR / "html" / "blessed-rose.html"


# ------------------------ #

def extract_flexible_labeled_value(soup, label):
    print(f"\n🔎 Searching for label: {label}")

    # Try: exact label span
    label_span = soup.find("span", string=lambda t: t and t.strip() == label)
    if label_span:
        print(f"  Label span: {label_span}")
        current = label_span
        for _ in range(5):  # scan ahead to catch weird formatting
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

    # Fallback: inline span with "Label: Value"
    inline_span = soup.find("span", string=lambda t: t and t.strip().startswith(label))
    if inline_span:
        print(f"  Inline span: {inline_span}")
        return inline_span.text.strip().replace(label, "").strip(" :.")

    print("  ❌ No match found")
    return None


def parse_meta_flora(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Name from meta
        title_tag = soup.find("meta", property="og:title")
        name = title_tag["content"].strip() if title_tag else "Unknown"

        # Meta description (if needed)
        desc_tag = soup.find("meta", property="og:description")
        desc_block = desc_tag["content"] if desc_tag else ""
        print(f"\n📝 Description meta: {desc_block[:100]}...")

        # Pull values with label logic
        availability = extract_flexible_labeled_value(soup, "Availability:")
        region = extract_flexible_labeled_value(soup, "Region:")
        preparation = extract_flexible_labeled_value(soup, "Preparation:")
        cost = extract_flexible_labeled_value(soup, "Cost:")
        description = extract_flexible_labeled_value(soup, "Description:")

        return {
            "name": name,
            "availability": availability,
            "region": region,
            "preparation": preparation,
            "cost": cost,
            "description": description
        }

    except Exception as e:
        print(f"💥 Failed to parse {file_path}: {e}")
        return None


if __name__ == "__main__":
    result = parse_meta_flora(TEST_FILE)
    if result:
        print("\n🌿 Parsed Flora Meta Info:")
        for k, v in result.items():
            print(f"  {k.title()}: {v}")
