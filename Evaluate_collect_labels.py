import json
import os
import pandas as pd

# File paths (EDIT THESE AS NEEDED)
group_label_file = "Data/GameTile/SemanticLabels/author_labeled_1_manual_group_labels.json"
affordance_file = "Data/GameTile/SemanticLabels/author_labeled_3_affordance_annotations.json"
supercategory_xlsx  = "Data/GameTile/group_supercategories.xlsx"
output_file = "Data/GameTile/object_annotations_author_combined.json"


# ======== Load Data ========
with open(group_label_file, 'r') as f:
    group_data = json.load(f)

affordance_data = {}
with open(affordance_file, 'r') as f:
    affordance_data = json.load(f)

supercategory_df = pd.read_excel(supercategory_xlsx)
group_to_super = {}
for _, row in supercategory_df.iterrows():
    group = str(row[1]).strip().lower()
    supercat = str(row[0]).strip()
    group_to_super[group] = supercat

# ======== Build Combined Annotation ========
combined_data = {}

for path, info in group_data.items():
    filename = os.path.normpath(path).split('complete_author_cleaned')[-1].lstrip("\\/")
    selected_groups = [g.lower() for g in info.get("selected_group_tokens", [])]
    supercategories = list({group_to_super[g] for g in selected_groups if g in group_to_super})
    affordance = affordance_data.get(filename, [])

    combined_data[filename] = {
        "detailed_name": info.get("detailed_name", ""),
        "selected_group_tokens": info.get("selected_group_tokens", []),
        "supercategories": supercategories,
        "affordance_labels": affordance
    }

# ======== Save Output ========
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False)

print(f"✅ Combined annotation written to {output_file}")