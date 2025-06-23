import json
import os
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk import download
from sentence_transformers import SentenceTransformer, util

# === NLTK setup ===
download('punkt')
download('wordnet')
download('omw-1.4')

# === FILES ===
INPUT_FILE = "Data/GameTile/caption_with_labels/captions_with_labels_author_swinir_x4.json"  # Or captions_with_labels_author_bicubic.json
OUTPUT_FILE = "Data/GameTile/caption_label_match_analysis_from_combined_author_swinir_x4.json"

# === Load input ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Model ===
print("🔍 Loading Sentence-BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Utilities ===
def get_tokens(text):
    return [w.lower() for w in word_tokenize(text) if w.isalnum()]

def get_synonyms(word):
    syns = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            syns.add(lemma.name().lower().replace("_", " "))
    return list(syns)

# === Matching ===
results = []
for entry in data:
    image_key = entry["image_key"]
    caption = entry.get("caption", "")
    tokens = get_tokens(caption)

    detailed_name = entry.get("detailed_name", "")
    group_labels = entry.get("group_labels", [])
    supercats = entry.get("supercategories", [])
    affordances = entry.get("affordance_labels", [])

    # === Direct match ===
    direct = {
        "group_labels": [g for g in group_labels if g.lower() in tokens],
        "supercategories": [s for s in supercats if s.lower() in tokens],
        "affordance_labels": [a for a in affordances if a.lower() in tokens]
    }

    # === Synonym match ===
    syn_matches = {
        "group_labels": [],
        "supercategories": [],
        "affordance_labels": []
    }
    for cat_type, labels in [("group_labels", group_labels), ("supercategories", supercats), ("affordance_labels", affordances)]:
        for label in labels:
            for syn in get_synonyms(label):
                if syn.lower() in tokens:
                    syn_matches[cat_type].append(syn)

    # === Semantic similarity ===
    label_phrases = list(set(group_labels + supercats + affordances + [detailed_name]))
    label_phrases = [l for l in label_phrases if l.strip()]

    if not caption.strip() or not label_phrases:
        top_semantic = []
    else:
        emb_caption = model.encode(caption, convert_to_tensor=True)
        emb_labels = model.encode(label_phrases, convert_to_tensor=True)
        scores = util.cos_sim(emb_caption, emb_labels)[0]
        top_semantic = sorted(
            [{"label": l, "score": round(scores[i].item(), 3)} for i, l in enumerate(label_phrases)],
            key=lambda x: -x["score"]
        )[:3]

    # === Result Entry ===
    results.append({
        "image_key": image_key,
        "caption": caption,
        "labels": {
            "detailed_name": detailed_name,
            "group_labels": group_labels,
            "supercategories": supercats,
            "affordance_labels": affordances
        },
        "matched_tokens": {
            "direct": direct,
            "synonyms": syn_matches,
            "semantic_similarity": top_semantic
        }
    })

# === Save ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Done. Results written to: {OUTPUT_FILE}")
