import json
import faiss
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from pathlib import Path

# ===================== Config =====================
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
INDEX_PATH = './shinseina_index.faiss'
META_PATH = './shinseina_metadata.json'
EMBED_MODEL = 'all-MiniLM-L6-v2'
PARAPHRASE_MODEL = 'facebook/bart-large-cnn'
TOP_K = 5
PARAPHRASE_COUNT = 4
MAX_LENGTH = 60

# ===================== Loaders =====================
print("🚀 Starting Shinseina Vector Search Setup...")

print("\n🔄 Loading:", end=" ", flush=True)
progress = tqdm(total=4)

# Load Metadata
with open(META_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)
progress.update(1)

# Load FAISS Index
index = faiss.read_index(INDEX_PATH)
progress.update(1)

# Load Embedding Model
embedder = SentenceTransformer(EMBED_MODEL)
progress.update(1)

# Load Paraphrasing Model
tokenizer = AutoTokenizer.from_pretrained(PARAPHRASE_MODEL)
paraphraser = AutoModelForSeq2SeqLM.from_pretrained(PARAPHRASE_MODEL).to(DEVICE)
progress.update(1)

progress.close()
print("✅ Done! Shinseina Vector Search Ready.\n")

# ===================== Paraphrase =====================
def generate_paraphrases(text, num_return_sequences=PARAPHRASE_COUNT):
    inputs = tokenizer([text], return_tensors="pt", max_length=MAX_LENGTH, truncation=True).to(DEVICE)
    output = paraphraser.generate(
        **inputs,
        max_length=MAX_LENGTH,
        num_return_sequences=num_return_sequences,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        early_stopping=True
    )
    return [tokenizer.decode(o, skip_special_tokens=True) for o in output]

# ===================== Search Function =====================
def search(query, top_k=TOP_K):
    print(f"🌀 Query: {query}\n")

    print("✨ Paraphrasing...")
    variants = generate_paraphrases(query)
    for idx, v in enumerate(variants):
        print(f"  ↳ Variant {idx+1}: {v}")

    all_queries = [query] + variants
    embeddings = embedder.encode(all_queries)
    avg_embedding = sum(embeddings) / len(embeddings)

    D, I = index.search(avg_embedding.reshape(1, -1), top_k)
    results = [metadata[i] for i in I[0]]
    return results

# ===================== Main =====================
if __name__ == '__main__':
    query = input("\n🔍 Enter your Shinseina query: ")
    top_k_results = search(query)

    print("\n🔍 Search Results:\n")
    for idx, item in enumerate(top_k_results):
        name = item.get("name", "Unknown")
        rarity = item.get("rarity", "Unknown")
        rank = item.get("rank", "Unknown")
        description = item.get("full_text", "").strip()
        url = item.get("url", "#")

        print(f"[{idx+1}] {name} ({rarity}, {rank})")
        print(f"     {description if description else '[❌ Missing Description]'}")
        print(f"     🔗 {url}\n")
