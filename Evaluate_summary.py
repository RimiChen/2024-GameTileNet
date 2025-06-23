import json
import os
from collections import defaultdict, Counter

# === Configurable Parameters ===
INPUT_PATH = "Data/GameTile/caption_label_match_analysis/caption_label_match_analysis_from_combined_author_swinir_x4.json"
OUTPUT_PATH = f"Data/GameTile/summary_{os.path.basename(INPUT_PATH)}"
SEMANTIC_THRESHOLD = 0.3

print("🔍 Loading and analyzing match data...")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

summary = defaultdict(Counter)
total_images = len(data)
summary["total"]["images"] = total_images

for entry in data:
    matched = entry.get("matched_tokens", {})
    labels = entry.get("labels", {})

    # Count direct matches
    for cat in ["group_labels", "supercategories", "affordance_labels"]:
        if matched.get("direct", {}).get(cat):
            summary["direct"][cat] += 1

    # Count synonym matches
    for cat in ["group_labels", "supercategories", "affordance_labels"]:
        if matched.get("synonyms", {}).get(cat):
            summary["synonym"][cat] += 1

    # Count semantic matches
    for match in matched.get("semantic_similarity", []):
        label = match.get("label", "")
        score = match.get("score", 0.0)
        if score >= SEMANTIC_THRESHOLD:
            for cat in ["group_labels", "supercategories", "affordance_labels"]:
                if label in labels.get(cat, []):
                    summary["semantic"][cat] += 1

# Save output
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print(f"✅ Summary complete. Total images: {total_images}")
print(f"📄 Results written to: {OUTPUT_PATH}")
