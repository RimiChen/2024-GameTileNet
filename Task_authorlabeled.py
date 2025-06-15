import os
import re
import json
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# ========== CONFIG ==========
input_root = r"Data/GameTile/complete_author"  # ← EDIT THIS
output_img_root = r"Data/GameTile/complete_author_cleaned"  # ← EDIT THIS
output_json_path = r"Data/GameTile/complete_author_json/cleaned_labels.json"  # ← EDIT THIS

# ========== UTILS ==========
def make_dirs(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def clean_background(image):
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    changed = False
    for item in datas:
        if item[:3] == (255, 0, 255):  # magenta
            newData.append((0, 0, 0, 0))
            changed = True
        else:
            newData.append(item)
    if changed:
        image.putdata(newData)
    return image, changed

def normalize_label(filename):
    base = Path(filename).stem
    base = re.sub(r'\d+', '', base)  # remove numbers
    base = re.sub(r'([a-z])([A-Z])', r'\1_\2', base)  # camelCase → camel_Case
    base = re.sub(r'[^a-zA-Z_]', '', base)  # remove other chars
    return base.lower()

# ========== MAIN ==========
metadata = []

for subdir, _, files in os.walk(input_root):
    rel_subdir = os.path.relpath(subdir, input_root)
    output_subdir = os.path.join(output_img_root, rel_subdir)
    make_dirs(output_subdir)

    for file in tqdm(files, desc=f"Processing {rel_subdir}"):
        if not file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            continue

        full_path = os.path.join(subdir, file)
        rel_path = os.path.relpath(full_path, input_root)
        label = normalize_label(file)

        filename_base = Path(file).stem
        output_img_path = os.path.join(output_subdir, filename_base + ".png")

        try:
            img = Image.open(full_path).convert("RGBA")
            cleaned_img, _ = clean_background(img)
            cleaned_img.save(output_img_path, format="PNG")
        except Exception as e:
            print(f"⚠️ Failed to process {full_path}: {e}")
            continue

        metadata.append({
            "original_filename": file,
            "relative_path": os.path.relpath(output_img_path, output_img_root),
            "cleaned_label": label,
            "subfolder": rel_subdir
        })

# ========== SAVE JSON ==========
make_dirs(os.path.dirname(output_json_path))
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("✅ Done. All images saved as PNG, metadata written.")
