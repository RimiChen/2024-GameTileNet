import os
from PIL import Image

# ======= Config =======
# INPUT_ROOT = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"  # e.g., input_tiles/folder_x/*.png
# OUTPUT_ROOT = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic"
# INPUT_ROOT = "Data/GameTile/complete_labels_output_model/complete"  # e.g., input_tiles/folder_x/*.png
# OUTPUT_ROOT = "Data/GameTile/complete_labels_output_model/upscaled_tiles/bicubic"
INPUT_ROOT = "Data/GameTile/complete_author_cleaned"  # e.g., input_tiles/folder_x/*.png
OUTPUT_ROOT = "Data/GameTile/complete_author_processed/bicubic"

TARGET_LONG_EDGE = 512       # Longest side will be resized to this
FILL_BACKGROUND = True
BACKGROUND_COLOR = (255, 255, 255)  # White background
# =======================

def add_background_if_needed(img):
    if img.mode == 'RGBA' and FILL_BACKGROUND:
        background = Image.new("RGB", img.size, BACKGROUND_COLOR)
        background.paste(img, mask=img.split()[3])  # Use alpha as mask
        return background
    elif img.mode != 'RGB':
        return img.convert("RGB")
    return img

def resize_proportionally(img, target_long_edge):
    w, h = img.size
    scale = target_long_edge / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    return img.resize((new_w, new_h), resample=Image.BICUBIC)

# Traverse folders and process images
for dirpath, _, filenames in os.walk(INPUT_ROOT):
    for fname in filenames:
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        in_path = os.path.join(dirpath, fname)
        rel_dir = os.path.relpath(dirpath, INPUT_ROOT)
        out_dir = os.path.join(OUTPUT_ROOT, rel_dir)
        os.makedirs(out_dir, exist_ok=True)

        img = Image.open(in_path)
        img = add_background_if_needed(img)
        img_upscaled = resize_proportionally(img, TARGET_LONG_EDGE)

        out_path = os.path.join(out_dir, fname)
        img_upscaled.save(out_path)
        print(f"[SAVE] {fname} → {out_path}")
