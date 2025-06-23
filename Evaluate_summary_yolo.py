# import json
# import os
# from collections import defaultdict
# import pandas as pd

# # === CONFIG ===
# input_files = {
#     "bicubic": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_bicubic.json",
#     "realesrgan": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_realesrgan_x4.json",
#     "sd_fidelity": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_sd_fidelity.json",
#     "sd_img2img": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_sd_img2img.json",
#     "swinir": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_swinir_x4.json"
# }
# output_csv = "Data/GameTile/yolo_label_comparison_table.csv"
# output_json = "Data/GameTile/yolo_label_comparison_table.json"

import os
import json
from collections import defaultdict
import pandas as pd

# Path to ground-truth labels
REFERENCE_LABEL_PATH = "Data/GameTile/object_annotations_author_combined_author_orginal.json"

# Detected object files per image source
input_files = {
    "bicubic": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_bicubic.json",
    "realesrgan": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_realesrgan_x4.json",
    "sd_fidelity": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_sd_fidelity.json",
    "sd_img2img": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_sd_img2img.json",
    "swinir": "Data/GameTile/yolo8m/yolo8m_detected_objects_author_swinir_x4.json",
}

# Load ground-truth reference labels
with open(REFERENCE_LABEL_PATH, "r", encoding="utf-8") as f:
    reference_data = json.load(f)

# Normalize keys: beings\\AlienBuyer.png -> beings/AlienBuyer.png
reference_labels = {
    "/".join(k.replace("\\", "/").split("/")[-2:]): set(v.get("group_label", []))
    for k, v in reference_data.items()
}

results = {}

for name, path in input_files.items():
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        detections_list = json.load(f)

    total_images = len(detections_list)
    images_with_yolo = 0
    total_detections = 0
    total_matches = 0
    images_with_match = 0

    for entry in detections_list:
        raw_path = entry.get("image_path", "")
        norm_path = raw_path.replace("\\", "/")
        img_key = "/".join(norm_path.split("/")[-2:])  # beings/DemonicWizard.png

        detected_objects = entry.get("objects", [])
        if not detected_objects:
            continue

        images_with_yolo += 1
        total_detections += len(detected_objects)

        gt_labels = reference_labels.get(img_key, set())
        detected_labels = set([obj["label"] for obj in detected_objects])
        matched = gt_labels & detected_labels

        if matched:
            total_matches += len(matched)
            images_with_match += 1

    precision = total_matches / total_detections if total_detections > 0 else 0

    result = {
        "total_images": total_images,
        "total_images_with_yolo_detection": images_with_yolo,
        "total_detections": total_detections,
        "total_matches": total_matches,
        "images_with_at_least_one_match": images_with_match,
        "overall_precision": round(precision, 3),
    }

    results[name] = result

    # Save each result
    output_path = f"summary_yolo8m_detected_objects_author_{name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"✅ [{name.upper()}] Summary written to {output_path}")

# Optionally print final summary table
df = pd.DataFrame(results).T
print("\n📊 Detection Summary Table:\n")
print(df)
