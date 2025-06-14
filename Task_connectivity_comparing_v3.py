# edge_transparency_compare_false.py
import os, json, pandas as pd

manual_file = "Data/GameTile/labeled_connectivity_manual.json"
predicted_folder = "Data/GameTile/connectivity_results_smart"
csv_out, json_out = "Data/GameTile/edge_transparency_false_match_smart.csv", "Data/GameTile/edge_transparency_false_match_smart.json"

# Load manual labels (assumed to represent expected solid edges)
with open(manual_file) as f: manual_labels = json.load(f)

# Parse manual edges from label directions
manual_map = {}
for path, labels in manual_labels.items():
    parts = path.replace(".png", "").replace("\\", "/").split("/")[-1].split("_")
    if len(parts) == 3:
        key = (path.split("\\")[0], int(parts[1]), int(parts[2]))
        manual_map[key] = set(labels)

# Load predicted edge transparency, extract edges marked False (non-transparent = solid)
predicted_map = {}
for fname in os.listdir(predicted_folder):
    if fname.endswith(".json") and fname.startswith("tile_connectivity-"):
        map_id = fname.replace("tile_connectivity-", "").replace(".json", "")
        with open(os.path.join(predicted_folder, fname)) as f:
            for tile in json.load(f):
                edge_t = tile.get("edge_transparency", {})
                solid_edges = {k for k, v in edge_t.items() if v is False}
                predicted_map[(map_id, tile["tile_x"], tile["tile_y"])] = solid_edges

# Compare solid (False) edges
results = []
for k, mset in manual_map.items():
    pset = predicted_map.get(k, set())
    tp = len(mset & pset); fp = len(pset - mset); fn = len(mset - pset)
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    results.append({
        "map": k[0], "tile_x": k[1], "tile_y": k[2],
        "manual_solid_edges": sorted(mset),
        "predicted_solid_edges": sorted(pset),
        "precision": round(prec, 2),
        "recall": round(rec, 2),
        "f1_score": round(f1, 2),
        "exact_match": mset == pset
    })

# Save
pd.DataFrame(results).to_csv(csv_out, index=False)
with open(json_out, "w") as f: json.dump(results, f, indent=2)
print("Corrected edge transparency (false edges) comparison complete.")
