import os
import random
import json

def sample_tiles_from_folders(root_dir, sample_size, output_file):
    all_tiles = []

    # Walk through all subfolders
    for subdir in sorted(os.listdir(root_dir)):
        subdir_path = os.path.join(root_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue

        # Collect .png files
        for fname in sorted(os.listdir(subdir_path)):
            if fname.lower().endswith(".png"):
                relative_path = os.path.join(subdir, fname)
                all_tiles.append(relative_path)

    print(f"Found {len(all_tiles)} tiles.")

    # Sample without replacement (use min if fewer tiles than requested)
    sampled = random.sample(all_tiles, min(sample_size, len(all_tiles)))

    # Save output
    with open(output_file, "w") as f:
        json.dump(sampled, f, indent=4)

    print(f"Saved {len(sampled)} sampled tiles to {output_file}")

# ==== USER CONFIG ====
tile_folder = "Data/GameTile/small_dataset/Tiles"
num_samples = 200  # Change this to how many tiles you want to sample
output_json = "Data/GameTile/connectivity_sampled_tiles.json"

# ==== RUN ====
sample_tiles_from_folders(tile_folder, num_samples, output_json)
