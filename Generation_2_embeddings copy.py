# build_embedding_index.py
import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Input and output
input_file = "Data/GameTile/combined_object_annotations.json"
output_file = "Data/GameTile/object_embedding_index.jsonl"

# Load data
with open(input_file, "r", encoding="utf-8") as f:
    objects = json.load(f)

# Function to encode text to vector
def get_embedding(text):
    return model.encode(text, show_progress_bar=False).tolist()

# Build JSONL with embeddings
with open(output_file, "w", encoding="utf-8") as fout:
    for obj in tqdm(objects, desc="Embedding objects"):
        entry = {
            "image_path": obj["image_path"],
            "detailed_name": obj["detailed_name"],
            "group": obj.get("group", []),
            "supercategory": obj.get("supercategory", []),
            "affordance": obj.get("affordance", []),
            "embedding": {
                "detailed_name": get_embedding(obj["detailed_name"]),
                "group": get_embedding(" ".join(obj.get("group", []))),
                "supercategory": get_embedding(" ".join(obj.get("supercategory", []))),
                "affordance": get_embedding(" ".join(obj.get("affordance", []))),
            }
        }
        fout.write(json.dumps(entry) + "\n")

print(f"[✓] Saved index to: {output_file}")
