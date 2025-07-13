import re
import json
from collections import defaultdict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

rank_map = {"d": 1, "c": 2, "b": 3, "a": 4, "s": 5, "common": 6, "uncommon": 7, "rare": 8, "rare+": 9, "legendary": 8,
            "legendary+": 9, "mythical": 10, "ex": 11}
metadata_list = []
texts_to_embed = []
id_counter = 0
reverse_map = defaultdict(list)
SKIP_KEYS = {"id", "name"}
JUNK_VALUES = {"n/a", "unknown", "none", "", "?"}
embedskip = {"id", "name", "region", "rank_value", "category"}

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("flora_final_clean.json", "r", encoding="utf-8") as f:
    flora_data = json.load(f)

with open("minerals_final_clean.json", "r", encoding="utf-8") as f:
    mineral_data = json.load(f)

def normalize_location(loc):
    if not loc:
        return "unknown"
    loc = str(loc).lower().strip()
    if loc in JUNK_VALUES:
        return "unknown"

    loc = re.sub(r"[^a-z\s]", "", loc)
    words = loc.split()
    ignore = {"the", "of", "in", "on", "between", "near", "to", "from", "around", "ridge"}
    clean_words = [w for w in words if w not in ignore]
    return " ".join(clean_words) if clean_words else "unknown"

def simplify_region(val):
    if not val: return "unknown"
    val = val.lower()
    if "forest" in val: return "forest"
    if "mountain" in val: return "mountain"
    if "swamp" in val: return "swamp"
    if "desert" in val: return "desert"
    if "ocean" in val or "reef" in val: return "ocean"
    return val

def metadata_sorter(data_dict, category):
    global id_counter
    for rarity, entries in data_dict.items():
        for entry in entries:
            metadata = dict(entry)
            metadata["rarity"] = rarity.lower()
            metadata["category"] = category
            metadata["region"] = simplify_region(normalize_location(entry.get("Location", "unknown")))
            metadata["id"] = id_counter
            metadata["rank_value"] = rank_map.get(metadata["rarity"], 0)
            metadata["rank"] = entry.get("Rank", "").strip().lower()

            text_parts = [metadata.get("name", "")]
            for k, v in metadata.items():
                if k not in embedskip:
                    v_clean = clean_value(v)
                    if v_clean is not None:
                        text_parts.append(f"{k}: {v_clean}")
            full_text = ". ".join(text_parts)

            metadata_list.append(metadata)
            texts_to_embed.append(full_text)
            print(f"✅ [{id_counter}] {metadata['name']}")
            id_counter += 1

def clean_value(val):
    val = str(val).strip().lower()
    return None if val in JUNK_VALUES else val

if __name__ == "__main__":
    metadata_sorter(flora_data, "flora")
    metadata_sorter(mineral_data, "mineral")

    # Save JSON data
    with open("texts_to_embed.json", "w", encoding="utf-8") as f:
        json.dump(texts_to_embed, f, ensure_ascii=False, indent=2)
    with open("metadata_list.json", "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    filter_map = {m["id"]: (m["rarity"], m["category"], m["region"]) for m in metadata_list}
    for m in metadata_list:
        for key in ["category", "rarity", "region", "rank"]:
            val = m.get(key)
            if val:
                reverse_map[val].append(m["id"])

    with open("filter_map.json", "w", encoding="utf-8") as f:
        json.dump(filter_map, f, ensure_ascii=False, indent=2)
    with open("reverse_map.json", "w", encoding="utf-8") as f:
        json.dump(dict(reverse_map), f, ensure_ascii=False, indent=2)

    # Embedding and FAISS
    embeddings = model.encode(texts_to_embed, show_progress_bar=True, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, "shin_vector.index")
    with open("index_metadata_map.json", "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
