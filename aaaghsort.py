import json

with open("shinseina_metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)
    print(json.dumps(meta[0], indent=2))