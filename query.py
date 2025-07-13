import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load index
index = faiss.read_index("shin_vector.index")

# Load metadata
with open("index_metadata_map.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Make sure this matches what you used during creation


def search_index(query, top_k=5):
    # Encode the query
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search the index
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(distances[0], indices[0]):
        entry = metadata[idx]
        results.append({
            "id": entry["id"],
            "name": entry.get("name", "???"),
            "category": entry.get("category", "???"),
            "rarity": entry.get("rarity", "???"),
            "region": entry.get("region", "???"),
            "score": float(score)
        })

    return results


# --- Example usage ---
if __name__ == "__main__":
    on = True
    while on:
        query = input("Enter your search query: ")
        results = search_index(query, top_k=5)

        print("\n--- Top Results ---")
        for r in results:
            print(f"[{r['id']}] {r['name']} ({r['category']}, {r['rarity']}, {r['region']}) | Score: {r['score']:.2f}")
        if input("Enter quit to quit ").lower() == "quit":
            on = False