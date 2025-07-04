import os
import json
import torch
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import pandas as pd
import sys
sys.path.append("D:/Github/2024-GameTileNet/GroundingDINO")  # <-- Add this before import
from groundingdino.util.inference import load_model, predict
from groundingdino.util.inference import load_image
from segment_anything import sam_model_registry, SamPredictor
from torchvision import transforms

print("Running updated DINO-SAM script ✅")

def preprocess_image(image_pil):
    transform = transforms.Compose([
        transforms.Resize((800, 800)),  # or (512, 512) if tiles are small
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return transform(image_pil).unsqueeze(0)  # (1, C, H, W)



# === CONFIG ===
EXCEL_PATH = "Data/GameTile/group_supercategories.xlsx"
PROMPT_COLUMN = "GROUP"
GROUNDING_DINO_CONFIG = "GroundingDINO/groundingdino/config/GroundingDINO_SwinB_cfg.py"
GROUNDING_DINO_WEIGHTS = "Data/groundingdino_swinb_cogcoor.pth"
SAM_WEIGHTS = "Data/sam_vit_h_4b8939.pth"
BOX_THRESHOLD = 0.3
TEXT_THRESHOLD = 0.25





def load_prompts_from_excel(filepath, column="GROUP"):
    df = pd.read_excel(filepath)
    prompts = df[column].dropna().unique().tolist()
    prompts = [p.strip() for p in prompts if isinstance(p, str) and p.strip()]
    print(f"Loaded {len(prompts)} unique prompts from '{column}' column.")
    return prompts


def setup_models():
    dino_model = load_model(GROUNDING_DINO_CONFIG, GROUNDING_DINO_WEIGHTS)
    sam = sam_model_registry["vit_h"](checkpoint=SAM_WEIGHTS)
    sam_predictor = SamPredictor(sam)
    return dino_model, sam_predictor


def detect_and_visualize(image_path, dino_model, sam_predictor, text_prompts, save_path=None):
    image_pil = Image.open(image_path).convert("RGB")
    image_tensor = preprocess_image(image_pil)
    image_pil_resized = image_pil
    image = np.array(image_pil_resized).copy()

    results = []
    CHUNK_SIZE = 50

    for i in range(0, len(text_prompts), CHUNK_SIZE):
        chunk = text_prompts[i:i+CHUNK_SIZE]
        caption = ", ".join(chunk)

        try:
            boxes, logits, phrases = predict(
                model=dino_model,
                image=image_tensor,
                caption=caption,
                box_threshold=BOX_THRESHOLD,
                text_threshold=TEXT_THRESHOLD
            )
        except Exception as e:
            print(f"⚠️ Chunk {i}-{i+CHUNK_SIZE} failed: {e}")
            continue

        boxes = boxes * torch.Tensor([
            image_pil_resized.width,
            image_pil_resized.height,
            image_pil_resized.width,
            image_pil_resized.height
        ])

        for box, label in zip(boxes, phrases):
            x1, y1, x2, y2 = map(int, box.tolist())
            results.append({"label": label, "bbox": [x1, y1, x2, y2]})
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, image)

    return results


def process_folder(input_dir, output_json, annotated_dir, excel_path):
    prompts = load_prompts_from_excel(excel_path)
    dino_model, sam_predictor = setup_models()
    input_dir = Path(input_dir)
    all_results = []

    for img_path in input_dir.rglob("*.*"):
        if img_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            continue
        print(f"Processing {img_path.name}...")

        save_img_path = Path(annotated_dir) / img_path.relative_to(input_dir)
        detections = detect_and_visualize(
            image_path=str(img_path),
            dino_model=dino_model,
            sam_predictor=sam_predictor,
            text_prompts=prompts,
            save_path=str(save_img_path)
        )
        all_results.append({
            "image_path": str(img_path.resolve()),
            "objects": detections
        })

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Detection results saved to {output_json}")


# === USAGE ===
if __name__ == "__main__":
    process_folder(
        input_dir="Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic",
        output_json="Data/GameTile/gdino_detection_from_excel.json",
        annotated_dir="Data/GameTile/gdino_detection_from_excel_bicubic",
        excel_path=EXCEL_PATH
    )
