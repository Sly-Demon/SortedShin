import re
import json
import faiss
from sentence_transformers import SentenceTransformer

valid_regions = set()
valid_rarities = set()
category_keywords = {
    "flora": {"flora", "plant", "tree", "flower", "bush", "vine"},
    "mineral": {"mineral", "ore", "rock", "crystal", "stone", "gem"}
}

# Load index
index = faiss.read_index("shin_vector.index")

# Load metadata
with open("index_metadata_map.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Load reverse map
with open("reverse_map.json", "r", encoding="utf-8") as f:
    reverse_map = json.load(f)

with open("filter_map.json", "r", encoding="utf-8") as f:
    filter_map = json.load(f)

for key in reverse_map:
    if key.startswith("region:"):
        valid_regions.add(key.split(":", 1)[1])
    elif key.startswith("rarity:"):
        valid_rarities.add(key.split(":", 1)[1])

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Make sure this matches what you used during creation


def prompt_query():
    return input("Enter your search query: ").strip()


def prompt_exit():
    return input("Type 'quit' to exit or press Enter to continue: ").lower().strip() == "quit"


def clean_semantic_query(query, filters):
    stripped_query = query.lower()
    for val in filters.values():
        stripped_query = stripped_query.replace(val.lower(), "")
    stripped_query = re.sub(r"\ball\b|\b\d+\b", "", stripped_query)
    return stripped_query.strip() or query


def handle_query_cycle():
    while True:
        query = prompt_query()
        if not query:
            print("❌ No query entered. Try again.\n")
            continue

        result_limit = extract_result_limit(query)
        filters = extract_filters_from_query(query, valid_regions, valid_rarities, category_keywords)
        semantic_part = clean_semantic_query(query, filters)

        results = search_index(semantic_part, top_k=result_limit, filters=filters)

        print("\n--- Top Results ---")
        if results:
            for r in results:
                print(
                    f"[{r['id']:>4}] {r['name']:<30} ({r['category']}, {r['rarity']}, {r['region']}) | Score: {r['score']:.2f}")

        else:
            print("⚠️ No results found.")

        if prompt_exit():
            break


def extract_result_limit(query):
    q = query.lower()
    if "all " in q or "all" == q.strip():
        return None  # special case: return everything that matches
    match = re.search(r"\b(\d+)\b", q)
    if match:
        return int(match.group(1))
    return 5  # default


def get_filtered_ids(filters):
    id_sets = []
    for key, value in filters.items():
        key = f"{key}:{value.lower()}"
        ids = reverse_map.get(key, [])
        id_sets.append(set(ids))
        if key not in reverse_map:
            print(f"⚠️ Filter key not found: {key}")

    if not id_sets:
        return None  # No filter applied = search full index

    # Intersection of all filter sets
    return set.intersection(*id_sets)


def extract_filters_from_query(query, valid_regions, valid_rarities, category_keywords):
    filters = {}

    q = query.lower()

    # Category detection
    for keyword in category_keywords["flora"]:
        if keyword in q:
            filters["category"] = "flora"
            break
    for keyword in category_keywords["mineral"]:
        if keyword in q:
            filters["category"] = "mineral"
            break

    # Rarity detection
    for rarity in valid_rarities:
        if rarity in q:
            filters["rarity"] = rarity
            break

    # Region detection
    for region in valid_regions:
        if re.search(rf"\b{re.escape(region)}\b", q):
            filters["region"] = region
            break

    return filters


def search_index(query, top_k=5, filters=None):
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search a wider net to allow post-filtering
    distances, indices = index.search(query_embedding, 100)

    allowed_ids = get_filtered_ids(filters or {})
    results = []

    for score, idx in zip(distances[0], indices[0]):
        entry = metadata[idx]
        if allowed_ids is not None and entry["id"] not in allowed_ids:
            continue

        results.append({
            "id": entry["id"],
            "name": entry.get("name", "???"),
            "category": entry.get("category", "???"),
            "rarity": entry.get("rarity", "???"),
            "region": entry.get("region", "???"),
            "score": float(score)
        })

        if top_k and len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    handle_query_cycle()
