import os

# Define base path and category folders
base_path = "data"
categories = {
    "flora": ["common", "uncommon", "rare", "rare_plus", "legendary", "legendary_plus", "mythical"],
    "minerals": ["common", "uncommon", "rare", "rare_plus", "legendary"],
    "fauna": ["ex", "ss", "s", "a", "b", "c", "d", "e", "f", "n_a"]
}

for category, subfolders in categories.items():
    cat_path = os.path.join(base_path, category)
    os.makedirs(cat_path, exist_ok=True)

    # Create masterlist placeholder
    masterlist_path = os.path.join(cat_path, "masterlist.txt")
    open(masterlist_path, "a").close()

    # Create rank/rarity folders with _links.txt inside
    for name in subfolders:
        folder_path = os.path.join(cat_path, name)
        os.makedirs(folder_path, exist_ok=True)
        link_file = os.path.join(folder_path, "_links.txt")
        open(link_file, "a").close()

print("✅ Folder structure created successfully.")
