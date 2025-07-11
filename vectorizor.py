import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === CONFIG ===
FLORA_PATH = 'flora_final_clean.json'
MINERAL_PATH = 'minerals_final_clean.json'
EMBED_MODEL = 'all-MiniLM-L6-v2'
OUTPUT_INDEX = 'shinseina_index.faiss'
OUTPUT_META = 'shinseina_metadata.json'

# === Load JSON ===
def load_data(filepath, source_type):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    entries = []
    for rarity, items in raw.items():
        for item in items:
            entry_id = f"{source_type}_{item['name'].lower().replace(' ', '_')}"
            text = f"{item['name']}\nUse: {item.get('Use', '')}\nLocation: {item.get('Location', '')}\n"
            text += f"Preparation: {item.get('Preparation', '')}\nCost: {item.get('Cost', '')}\nLegality: {item.get('Legality', '')}\n"
            text += f"Notes: {item.get('Additional Notes', '')}"

            entries.append({
                'id': entry_id,
                'text': text.strip(),
                'metadata': {
                    'name': item['name'],
                    'rarity': rarity,
                    'source': source_type,
                    'link': item.get('Link', ''),
                    'full_text': text.strip()  # 🔥 this is the key change
                }
            })
    return entries

# === Step 1: Load and combine ===
flora = load_data(FLORA_PATH, 'flora')
minerals = load_data(MINERAL_PATH, 'mineral')
entries = flora + minerals

# === Step 2: Generate embeddings ===
model = SentenceTransformer(EMBED_MODEL)
texts = [e['text'] for e in entries]
print("Generating embeddings... This may take a moment.")
embeddings = model.encode(texts, show_progress_bar=True)

# === Step 3: Build FAISS index ===
dim = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype('float32'))

# === Step 4: Save index and metadata ===
faiss.write_index(index, OUTPUT_INDEX)

with open(OUTPUT_META, 'w', encoding='utf-8') as f:
    json.dump([e['metadata'] for e in entries], f, indent=2)

print(f"\n✅ Rebuild complete!\nIndex: {OUTPUT_INDEX}\nMetadata: {OUTPUT_META}")
