import os
import json

# === Configure these paths ===
label_file = 'Data/GameTile/SemanticLabels/author_labeled_1_manual_group_labels.json'
caption_file = 'Data/GameTile/vlm_author_labeled_tiles/vlm_caption_results_author_original.json'
output_file = 'Data/GameTile/author_caption_comparison_original.json'

label_root_prefix = 'Data/GameTile/complete_author_cleaned'
caption_root_prefix = 'Data/GameTile/complete_author_cleaned'

# === Load files ===
with open(label_file, 'r', encoding='utf-8') as f:
    label_data = json.load(f)

with open(caption_file, 'r', encoding='utf-8') as f:
    caption_data = json.load(f)

# === Normalize and build caption map ===
caption_map = {}
for entry in caption_data:
    full_path = os.path.normpath(entry['image'])
    if caption_root_prefix in full_path:
        rel_path = os.path.normpath(full_path.split(caption_root_prefix)[-1].lstrip("\\/"))
        caption_map[rel_path] = entry['caption']
    else:
        print(f"⚠️ Caption entry path does not contain prefix: {full_path}")

# === Match with labels ===
comparison = {}
matched = 0
for full_path, label_info in label_data.items():
    norm_path = os.path.normpath(full_path)
    if label_root_prefix in norm_path:
        rel_path = os.path.normpath(norm_path.split(label_root_prefix)[-1].lstrip("\\/"))
    else:
        print(f"⚠️ Label entry path does not contain prefix: {norm_path}")
        continue

    caption = caption_map.get(rel_path, None)
    if caption: matched += 1

    comparison[rel_path] = {
        "detailed_name": label_info.get("detailed_name", ""),
        "selected_group_tokens": label_info.get("selected_group_tokens", []),
        "caption": caption
    }

# === Save results ===
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(comparison, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(comparison)} entries to {output_file}")
print(f"📌 {matched} out of {len(comparison)} had a caption match")
