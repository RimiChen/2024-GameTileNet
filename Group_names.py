import json
import os
import re
from collections import Counter, defaultdict
import nltk
from nltk import pos_tag

# Manually defined simple English stopwords (can be extended)
manual_stopwords = set([
    "a", "an", "the", "of", "to", "in", "on", "at", "for", "with", "and", "or", "by", "as", "from"
])

# Load JSON file
with open("Data/GameTile/complete_author_json/cleaned_labels.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Load preserved words
import pandas as pd
preserved_df = pd.read_csv("Data/GameTile/output_files_preserved_name.csv")
preserved_words = set()
for name in preserved_df.iloc[:, 0]:
    tokens = re.split(r"[\s_\-\.]+", str(name).lower())
    preserved_words.update(tokens)

# Frequency count
all_tokens = []
for entry in data:
    tokens = re.split(r"[\s_\-\.]+", entry["cleaned_label"].lower())
    all_tokens.extend(tokens)
token_freq = Counter(all_tokens)

# Group label extractor
def extract_group_name(name):
    tokens = re.split(r"[\s_\-\.]+", name.lower())
    tokens = [t for t in tokens if t not in manual_stopwords and len(t) > 1]

    if not tokens:
        return name

    tagged = pos_tag(tokens)
    noun_candidates = [word for word, tag in tagged if tag.startswith("NN")]

    # Priority 1: noun in preserved list
    for noun in noun_candidates:
        if noun in preserved_words:
            return noun

    # Priority 2: most frequent noun
    if noun_candidates:
        return sorted(noun_candidates, key=lambda w: -token_freq[w])[0]

    # Priority 3: any preserved token
    for t in tokens:
        if t in preserved_words:
            return t

    # Fallback: most frequent token
    return sorted(tokens, key=lambda w: -token_freq[w])[0]

# Apply and store results
results = []
group_counter = Counter()

for entry in data:
    detailed = entry["cleaned_label"]
    rel_path = entry["relative_path"].replace("\\", "/")
    full_path = os.path.join("Data/GameTile", rel_path)
    group = extract_group_name(detailed)
    group_counter[group] += 1
    results.append({
        "path": full_path,
        "detailed_name": detailed,
        "group_label": group,
        "affordance_label": []
    })

# Output JSON
with open("Data/GameTile/complete_author_json/annotated_labels.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# Output summary
group_summary = {
    "group_counts": dict(group_counter),
    "unique_groups": sorted(group_counter.keys())
}
with open("Data/GameTile/complete_author_json/group_summary.json", "w", encoding="utf-8") as f:
    json.dump(group_summary, f, indent=2)

print("Finished. Annotated data written to 'annotated_labels.json'. Group summary in 'group_summary.json'.")
