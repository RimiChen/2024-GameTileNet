import os
import json
import os
import json

def save_png_lists_by_subfolder(folder_path, out_path):
    print(f"Scanning: {folder_path}\n")

    # Create the output directory if it doesn't exist
    os.makedirs(out_path, exist_ok=True)

    for subfolder in sorted(os.listdir(folder_path)):
        subfolder_path = os.path.join(folder_path, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        # List .png files in the subfolder
        png_files = sorted([
            os.path.join(subfolder_path, f)
            for f in os.listdir(subfolder_path)
            if f.lower().endswith('.png')
        ])

        # Output file path in the output folder
        output_file = os.path.join(out_path, f"{subfolder}_tiles.json")

        # Save as JSON
        with open(output_file, 'w') as f:
            json.dump(png_files, f, indent=4)

        print(f"Saved {len(png_files)} paths to: {output_file}")

# Example usage
FOLDER = "bk_small_dataset/No_Reduce_Segments"
# FOLDER = "small_Segmenets_model"
folder_path = "Data/GameTile/" + FOLDER
# out_path = "Data/GameTile/small_Segments/model/"
out_path = "Data/GameTile/small_Segments/algo/"

save_png_lists_by_subfolder(folder_path, out_path)
