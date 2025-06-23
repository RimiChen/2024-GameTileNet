import json
import os

# === Input JSON files ===
author_file = "Data/GameTile/object_annotations_author_combined_author_orginal.json"
manual_file = "Data/GameTile/object_annotations_recursive.json"

# === Path settings ===
author_root = "Data/GameTile/complete_author_processed/realesrgan_x4/"
manual_old_prefix = "Data/GameTile/complete_labels_output_algo_no_reduce/complete/"
manual_new_prefix = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/realesrgan_x4/"

# === Output JSON file ===
output_json = "Data/GameTile/affordance_dataset.json"

# === Load data ===
with open(author_file, "r", encoding="utf-8") as f:
    author_data = json.load(f)

with open(manual_file, "r", encoding="utf-8") as f:
    manual_data = json.load(f)

# === Combine and process ===
combined_data = []
source_count = {"author": 0, "manual": 0}

for image_path, entry in {**author_data, **manual_data}.items():
    # Get affordance labels
    labels = entry.get("affordance_labels") or entry.get("affordance_label") or []
    if isinstance(labels, str):
        labels = [labels]
    if not labels or not isinstance(labels, list):
        continue

    # Determine source and adjust image path
    if image_path in manual_data:
        source = "manual"
        img_path = image_path.replace("\\", "/")
        if img_path.startswith(manual_old_prefix):
            img_path = img_path.replace(manual_old_prefix, manual_new_prefix)
    else:
        source = "author"
        img_path = os.path.join(author_root, image_path.replace("\\", "/"))

    source_count[source] += 1
    combined_data.append({
        "image_path": img_path,
        "affordance_labels": sorted(set(labels)),  # Keep as list
        "source": source
    })

# === Save dataset ===
os.makedirs(os.path.dirname(output_json), exist_ok=True)
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=2)

print(f"✅ Dataset saved to {output_json} with {len(combined_data)} labeled samples.")
print(f"🔢 Author-labeled: {source_count['author']} | Manual-labeled: {source_count['manual']}")
