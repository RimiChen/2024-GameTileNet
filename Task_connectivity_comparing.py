# connectivity_comparison.py
import os, json, pandas as pd

manual_file = "Data/GameTile/labeled_connectivity_manual.json"
predicted_folder = "Data/GameTile/connectivity_results_smart"
csv_out, json_out = "Data/GameTile/connectivity_match_report_smart.csv", "Data/GameTile/connectivity_match_report_smart.json"

with open(manual_file) as f: manual_labels = json.load(f)
manual_map = {}
for path, labels in manual_labels.items():
    parts = path.replace(".png", "").replace("\\", "/").split("/")[-1].split("_")
    if len(parts) == 3:
        key = (path.split("\\")[0], int(parts[1]), int(parts[2]))
        manual_map[key] = set(labels)

predicted_map = {}
for fname in os.listdir(predicted_folder):
    if fname.endswith(".json"):
        key_id = fname.replace("tile_connectivity-", "").replace(".json", "")
        with open(os.path.join(predicted_folder, fname)) as f:
            for tile in json.load(f):
                predicted_map[(key_id, tile["tile_x"], tile["tile_y"])] = set(tile.get("connectivity", []))

results = []
for k, mset in manual_map.items():
    pset = predicted_map.get(k, set())
    tp = len(mset & pset); fp = len(pset - mset); fn = len(mset - pset)
    prec = tp / (tp+fp) if tp+fp else 0
    rec = tp / (tp+fn) if tp+fn else 0
    f1 = 2*prec*rec/(prec+rec) if prec+rec else 0
    results.append({"map": k[0], "tile_x": k[1], "tile_y": k[2],
        "manual": sorted(mset), "predicted": sorted(pset),
        "precision": round(prec,2), "recall": round(rec,2), "f1_score": round(f1,2),
        "exact_match": mset == pset})

df = pd.DataFrame(results)
df.to_csv(csv_out, index=False)
with open(json_out, "w") as f: json.dump(results, f, indent=2)
print("Connectivity comparison complete.")
