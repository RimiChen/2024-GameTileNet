import os
import json

# === Input and output folders ===
INPUT_FOLDER = "Data/GameTile/connectivity_results_smart"
OUTPUT_FOLDER = "Data/GameTile/connectivity_cleaned"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Process all JSON files ===
for fname in os.listdir(INPUT_FOLDER):
    if not fname.endswith(".json"):
        continue

    input_path = os.path.join(INPUT_FOLDER, fname)
    with open(input_path, "r") as f:
        tiles = json.load(f)

    # Update connectivity based on non-transparent edges
    for tile in tiles:
        tile["connectivity"] = [
            direction for direction, transparent in tile.get("edge_transparency", {}).items()
            if not transparent
        ]

    # Save to output
    output_path = os.path.join(OUTPUT_FOLDER, fname)
    with open(output_path, "w") as f:
        json.dump(tiles, f, indent=2)

    print(f"[SAVE] {fname} → {output_path}")

print("✅ All cleaned connectivity files saved.")
