# query_object_match.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

# Load model and index
model = SentenceTransformer('all-MiniLM-L6-v2')
index_file = "Data/GameTile/object_embedding_index.jsonl"

with open(index_file, "r", encoding="utf-8") as f:
    index = [json.loads(line) for line in f]

def get_embedding(text):
    return model.encode(text, show_progress_bar=False)

def cosine_sim(a, b):
    return 1 - cosine(a, b)

def query_object(query_text, top_k=3):
    query_vec = get_embedding(query_text)

    results = []
    for obj in index:
        sim_name = cosine_sim(query_vec, obj["embedding"]["detailed_name"])
        sim_group = cosine_sim(query_vec, obj["embedding"]["group"]) if obj["embedding"]["group"] else 0
        sim_super = cosine_sim(query_vec, obj["embedding"]["supercategory"]) if obj["embedding"]["supercategory"] else 0
        sim_afford = cosine_sim(query_vec, obj["embedding"]["affordance"]) if obj["embedding"]["affordance"] else 0

        # Weighted sum
        total_score = 0.4 * sim_name + 0.3 * sim_group + 0.2 * sim_super + 0.1 * sim_afford
        results.append((total_score, obj))

    results.sort(reverse=True, key=lambda x: x[0])
    return results[:top_k]

# Example
if __name__ == "__main__":
    query = "Statue of Liberty's crown"
    matches = query_object(query)
    for score, match in matches:
        print(f"[{score:.2f}] {match['detailed_name']} -> {match['image_path']}")
