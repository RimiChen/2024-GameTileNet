import os
from PIL import Image
import torch
from tqdm import tqdm

failed_images = []

def process_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to(device)  # Ensure correct shape
        with torch.no_grad():
            output = model(img_tensor)  # Assuming you have loaded SwinIR as `model`
        return output
    except Exception as e:
        return str(e)

root_folder = "Data/GameTile/complete_author_cleaned"
debug_log = {}

for category in os.listdir(root_folder):
    category_path = os.path.join(root_folder, category)
    if not os.path.isdir(category_path):
        continue

    debug_log[category] = {
        "processed": 0,
        "failed": 0,
        "fail_list": [],
        "errors": {}
    }

    for img_file in tqdm(os.listdir(category_path), desc=category):
        img_path = os.path.join(category_path, img_file)
        result = process_image(img_path)
        if isinstance(result, str):  # An error message
            debug_log[category]["failed"] += 1
            debug_log[category]["fail_list"].append(img_file)
            debug_log[category]["errors"][img_file] = result
        else:
            debug_log[category]["processed"] += 1

# Save debug log
import json
with open("swinir_debug_error_log.json", "w") as f:
    json.dump(debug_log, f, indent=2)
