import json
import os

# File paths
manual_file = "Data/GameTile/object_annotations_recursive.json"
author_file = "Data/GameTile/object_annotations_author_combined_author_orginal.json"
output_file = "Data/GameTile/combined_object_annotations.json"

# Root to strip from manual paths
manual_root_prefix = "Data/GameTile/complete_labels_output_algo_no_reduce/complete/"

# Load files
with open(manual_file, "r", encoding="utf-8") as f:
    manual_data = json.load(f)

with open(author_file, "r", encoding="utf-8") as f:
    author_data = json.load(f)

combined = []

# Process manual annotations
# for raw_path, data in manual_data.items():
#     # Normalize path by stripping prefix and replacing backslashes
#     clean_path = raw_path.replace(manual_root_prefix, "").replace("\\", "/")
#     entry = {
#         "image_path": clean_path,
#         "detailed_name": data["detailed_name"][0] if isinstance(data["detailed_name"], list) else data["detailed_name"],
#         "group": data.get("group_label", []),
#         "supercategory": data.get("supercategory", []),
#         "affordance": data.get("affordance_label", []),
#         "source": "manual"
#     }
#     combined.append(entry)
# Process manual annotations
for raw_path, data in manual_data.items():
    normalized_path = raw_path.replace("\\", "/")
    clean_path = normalized_path.replace(manual_root_prefix.replace("\\", "/"), "")
    entry = {
        "image_path": clean_path,
        "detailed_name": data["detailed_name"][0] if isinstance(data["detailed_name"], list) else data["detailed_name"],
        "group": data.get("group_label", []),
        "supercategory": data.get("supercategory", []),
        "affordance": data.get("affordance_label", []),
        "source": "manual"
    }
    combined.append(entry)


# Process author annotations
for raw_path, data in author_data.items():
    clean_path = raw_path.replace("\\", "/")
    entry = {
        "image_path": clean_path,
        "detailed_name": data["detailed_name"],
        "group": data.get("selected_group_tokens", []),
        "supercategory": data.get("supercategories", []),
        "affordance": data.get("affordance_labels", []),
        "source": "author"
    }
    combined.append(entry)

# Save output
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"[✓] Combined {len(combined)} entries into {output_file}")
