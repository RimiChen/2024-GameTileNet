import os
import json
import cv2
from PIL import Image
from pathlib import Path
import torch
from torchvision import transforms

# Optional: use YOLOv5 for object detection
try:
    from ultralytics import YOLO
    MODEL = YOLO("yolov8m.pt")  # switch model as needed
    USE_YOLO = True
except ImportError:
    print("YOLO model not found, fallback to dummy detection.")
    USE_YOLO = False


def detect_objects_yolo(image_path):
    results = MODEL(image_path)
    boxes = results[0].boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
    names = results[0].names
    cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)
    return [{"label": names[int(cls)], "bbox": box.tolist()} for cls, box in zip(cls_ids, boxes)]


def dummy_detector(image_path):
    # Placeholder for simple or test detectors
    return [{"label": "unknown_object", "bbox": [10, 10, 100, 100]}]


def detect_objects(image_path, method="yolo"):
    if method == "yolo" and USE_YOLO:
        return detect_objects_yolo(image_path)
    else:
        return dummy_detector(image_path)


def save_annotated_image(image_path, objects, save_path):
    image = cv2.imread(str(image_path))
    for obj in objects:
        x1, y1, x2, y2 = map(int, obj["bbox"])
        label = obj["label"]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(str(save_path), image)


def process_folder(root_folder, output_json, output_annotated_dir, method="yolo"):
    root_folder = Path(root_folder)
    result = []

    for img_path in root_folder.rglob("*.*"):
        if img_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            continue

        objects = detect_objects(str(img_path), method)
        record = {
            "image_path": str(img_path.resolve()),
            "objects": objects
        }
        result.append(record)

        if output_annotated_dir:
            out_img_path = Path(output_annotated_dir) / img_path.relative_to(root_folder)
            out_img_path.parent.mkdir(parents=True, exist_ok=True)
            save_annotated_image(img_path, objects, out_img_path)

    with open(output_json, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved detection results to {output_json}")


# ---- Example usage ----
if __name__ == "__main__":
    process_folder(
        # root_folder="Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic",
        root_folder="Data/GameTile/complete_author_processed/sd_img2img",
        output_json="Data/GameTile/yolo8m_detected_objects_author_sd_img2img.json",
        output_annotated_dir="Data/GameTile/yolo8m_object_annotated_tiles_author_sd_img2img",
        method="yolo"  # or "dummy"
    )
