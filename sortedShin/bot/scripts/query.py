import re
import json
import faiss
from sentence_transformers import SentenceTransformer
from fragment_parser import detect_fragments

valid_regions = set()
valid_rarities = set()
category_keywords = {
    "flora": {"flora", "floras", "plants", "plant", "tree", "flowers", "flower", "bush", "vine"},
    "mineral": {"mineral", "ore", "rock", "crystal", "stone", "gem", "material"}
}

# Load index
index = faiss.read_index("shin_vector.index")

# Load metadata
with open("index_metadata_map.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Load reverse map
with open("reverse_map.json", "r", encoding="utf-8") as f:
    reverse_map = json.load(f)

# load map
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
    return input("Type 'quit' to quit or press Enter to continue: ").lower().strip() == "quit"

def extract_fragments(query: str):
    query = query.lower().strip()
    dividers = ['when', 'if', 'that', 'which', 'who', 'and', 'but', 'or', 'because', 'so']
    for divider in dividers:
        query = query.replace(f" {divider} ", f" || {divider} ")
    raw_fragments = re.split(r'\|\||,|\.', query)
    fragments = [frag.strip() for frag in raw_fragments if frag.strip()]
    return fragments

def clean_semantic_query(query, filters):
    stripped_query = query.lower()
    for val in filters.values():
        stripped_query = stripped_query.replace(val.lower(), "")
    stripped_query = re.sub(r"\ball\b|\b\d+\b", "", stripped_query)
    return stripped_query.strip() or query
def query(query = None):

    if query is None:
        query = prompt_query()

    if not query:
        print("No query entered. Try again.\n")
        return

    result_limit = extract_result_limit(query)
    filters = extract_filters_from_query(query, valid_regions, valid_rarities, category_keywords)
    semantic_part = clean_semantic_query(query, filters)
    if not semantic_part.strip():
        semantic_part = query.strip()

    fragments = detect_fragments(semantic_part)

    all_results = []

    for fragment in fragments if fragments else [semantic_part]:
        results = search_index(fragment, top_k=result_limit, filters=filters)
        all_results.extend(results)
    # merge results
    merged = {}
    for result in all_results:
        rid = result["id"]
        if rid in merged:
            merged[rid]["score"] += result["score"]
            merged[rid]["count"] += 1
        else:
            result["count"] = 1
            merged[rid] = result

    final_results = list(merged.values())
    for r in final_results:
        r["score"] /= r["count"]  # average it

    final_results.sort(key=lambda r: r["score"])  # sort best to worst

    if result_limit:
        final_results = final_results[:result_limit]
    return final_results


def handle_query_cycle():
    while True:
        final_results = query()

        if __name__ == "__main__":
            print("\n--- Top Results ---")
            if final_results:
                for r in final_results:
                    print(
                        f"[{r['id']:>4}] {r['name']:<30} ({r['category']}, {r['rarity']}, {r['region']}) | Score: {r['score']:.2f}")
            else:
                print("No results found.")

        if prompt_exit():
            break


def extract_result_limit(query):
    q = query.lower()
    if "all " in q or "all" == q.strip():
        return None
    match = re.search(r"\b(\d+)\b", q)
    if match:
        return int(match.group(1))
    if "the" in q.lower() or "the" == q.strip:
        return 1
    return 5

def get_filtered_ids(filters):
    id_sets = []
    for key, value in filters.items():
        key = f"{key}:{value.lower()}"
        ids = reverse_map.get(key, [])
        id_sets.append(set(ids))
        if key not in reverse_map:
            print(f"Filter key not found: {key}")

    if not id_sets:
        return None
    return set.intersection(*id_sets)

def extract_filters_from_query(query, valid_regions, valid_rarities, category_keywords):
    filters = {}
    q = query.lower()

    for keyword in category_keywords["flora"]:
        if keyword in q:
            filters["category"] = "flora"
            break
    for keyword in category_keywords["mineral"]:
        if keyword in q:
            filters["category"] = "mineral"
            break

    for rarity in valid_rarities:
        if rarity in q:
            filters["rarity"] = rarity
            break

    for region in valid_regions:
        if re.search(rf"\b{re.escape(region)}\b", q):
            filters["region"] = region
            break

    return filters

def search_index(query, top_k=5, filters=None):
    if not query.strip():
        return []

    try:
        query_embedding = model.encode([query], convert_to_numpy=True)
    except Exception as e:
        print(f" Error encoding query: {query} → {e}")
        return []

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
            "score": float(score),
            "link": entry.get("Link", None)
        })

        if top_k and len(results) >= top_k:
            break

    return results

if __name__ == "__main__":
    handle_query_cycle()