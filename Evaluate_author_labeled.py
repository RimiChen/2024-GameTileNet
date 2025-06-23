import os
import json

print("🚀 Starting caption-label comparison...")

# # === CONFIGURABLE PATHS ===
# caption_file = 'Data/GameTile/vlm_author_labeled_tiles/vlm_caption_results_author_original.json'
# label_info_file = 'Data/GameTile/object_annotations_author_combined_orginal.json'
# output_file = 'Data/GameTile/comparison_captions_with_labels_original.json'

# # === EDITABLE ROOT PREFIXES (must match the roots in caption/label file paths) ===
# caption_root_prefix = 'Data/GameTile/complete_author_cleaned'
# label_root_prefix = 'Data/GameTile/complete_author_cleaned'
import os
import json

# === PATH CONFIGURATION ===
CAPTION_JSON_PATH = "Data/GameTile/vlm_author_labeled_tiles/vlm_caption_results_author_swinir_x4.json"  # or original
ANNOTATION_JSON_PATH = "Data/GameTile/object_annotations_author_combined_orginal.json"
OUTPUT_JSON_PATH = "Data/GameTile/captions_with_labels_author_swinir_x4.json"

# import os
# import json

# # === ✅ CONFIGURABLE PATHS ===
# CAPTION_JSON_PATH = "vlm_caption_results_author_bicubic.json"  # or use the 'original' version
# ANNOTATION_JSON_PATH = "object_annotations_author_combined_orginal.json"
# OUTPUT_JSON_PATH = "comparison_captions_with_labels_fixed.json"

# === 🔧 HELPER FUNCTION ===
def normalize_path(full_path):
    # Extract subfolder/image_name from full path
    return "/".join(full_path.replace("\\", "/").split("/")[-2:])

# === 🚀 LOAD FILES ===
print("🔍 Loading files...")
with open(CAPTION_JSON_PATH, "r", encoding="utf-8") as f:
    caption_data = json.load(f)

with open(ANNOTATION_JSON_PATH, "r", encoding="utf-8") as f:
    annotation_data = json.load(f)

# Normalize keys in annotation dict for lookup
normalized_annotations = {}
for key, value in annotation_data.items():
    normalized_key = key.replace("\\", "/")  # e.g., beings/AlienBuyer.png
    normalized_annotations[normalized_key] = value

# === 🧠 COMBINE CAPTIONS WITH LABELS ===
results = []

for entry in caption_data:
    full_path = entry["image"]
    image_key = normalize_path(full_path)

    label_entry = normalized_annotations.get(image_key, {})
    results.append({
        "image_key": image_key,
        "caption": entry["caption"],
        "detailed_name": label_entry.get("detailed_name", ""),
        "group_labels": label_entry.get("selected_group_tokens", []),
        "supercategories": label_entry.get("supercategories", []),
        "affordance_labels": label_entry.get("affordance_labels", [])
    })

# === 💾 SAVE OUTPUT ===
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Comparison completed. Saved to: {OUTPUT_JSON_PATH}")
