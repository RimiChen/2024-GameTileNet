import os
import json

# List of root directories to check
### author pre-labeled images
# folders_to_check = [
#     "Data/GameTile/complete_author_cleaned",
#     "Data/GameTile/complete_author_processed/bicubic",
#     "Data/GameTile/complete_author_processed/swinir_x4",
#     "Data/GameTile/complete_author_processed/realesrgan_x4",
#     "Data/GameTile/complete_author_processed/sd_fidelity",
#     "Data/GameTile/complete_author_processed/sd_img2img",
# ]

### segmented images
folders_to_check = [
    "Data/GameTile/complete_labels_output_algo_no_reduce/complete",
    "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic",
    "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/swinir_x4",
    "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/realesrgan_x4",
    "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/sd_fidelity",
    "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/sd_img2img",
]




# Allowed image file extensions
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

# Dictionary to store the counts
result = {}

# Count images per subfolder
for folder in folders_to_check:
    folder_result = {}
    total_images = 0

    if not os.path.exists(folder):
        folder_result["__error__"] = "Folder does not exist"
        result[folder] = folder_result
        continue

    for subdir, _, files in os.walk(folder):
        img_count = sum(1 for f in files if os.path.splitext(f)[1].lower() in IMAGE_EXTS)
        if img_count > 0:
            rel_path = os.path.relpath(subdir, folder)
            folder_result[rel_path] = img_count
            total_images += img_count

    folder_result["__total__"] = total_images
    result[folder] = folder_result

# Write to JSON
output_path = "image_counts_by_folder.json"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"✅ Image counts saved to {output_path}")
