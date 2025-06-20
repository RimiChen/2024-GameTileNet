import os
import json
import torch
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import sys
sys.path.append("D:/Github/2024-GameTileNet/GroundingDINO")

from groundingdino.util.inference import load_model, predict
from segment_anything import sam_model_registry, SamPredictor
from torchvision import transforms

print("Running minimal debug version ✅")

# === CONFIG ===
TEST_IMAGE_PATH = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic/000_001_complete/combined_0_14.png"
GROUNDING_DINO_CONFIG = "GroundingDINO/groundingdino/config/GroundingDINO_SwinB_cfg.py"
GROUNDING_DINO_WEIGHTS = "Data/groundingdino_swinb_cogcoor.pth"
SAM_WEIGHTS = "Data/sam_vit_h_4b8939.pth"
BOX_THRESHOLD = 0.3
TEXT_THRESHOLD = 0.25
DEBUG_PROMPTS = ["tree", "rock", "flower", "sword", "shield", "chest"]

def preprocess_image(image_pil):
    transform = transforms.Compose([
        transforms.Resize((800, 800)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return transform(image_pil).unsqueeze(0)

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
    caption = ", ".join(text_prompts)

    try:
        boxes, logits, phrases = predict(
            model=dino_model,
            image=image_tensor,
            caption=caption,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD
        )
    except Exception as e:
        print(f"⚠️ Detection failed: {e}")
        return []

    if boxes is None or len(boxes) == 0:
        print("⚠️ No boxes detected.")
        return []

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

# === RUN ===
# if __name__ == "__main__":
#     dino_model, sam_predictor = setup_models()

#     detections = detect_and_visualize(
#         image_path=TEST_IMAGE_PATH,
#         dino_model=dino_model,
#         sam_predictor=sam_predictor,
#         text_prompts=DEBUG_PROMPTS,
#         save_path="Data/GameTile/debug_output/annotated_combined_0_14.png"
#     )

#     print(f"✅ Detected {len(detections)} objects")
#     print(json.dumps(detections, indent=2))


# Add this to the bottom of Task_objectDetection_DINO_SAM_debug.py

from pathlib import Path

DEBUG_INPUT_FOLDER = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic"
DEBUG_OUTPUT_FOLDER = "Data/GameTile/debug_output/folder_test"

if __name__ == "__main__":
    dino_model, sam_predictor = setup_models()

    image_paths = list(Path(DEBUG_INPUT_FOLDER).rglob("*.png"))
    print(f"🔍 Found {len(image_paths)} images to process.")

    for img_path in image_paths:
        relative_path = img_path.relative_to(DEBUG_INPUT_FOLDER)
        save_path = Path(DEBUG_OUTPUT_FOLDER) / relative_path
        print(f"🖼️ Processing {img_path.name}")

        detections = detect_and_visualize(
            image_path=str(img_path),
            dino_model=dino_model,
            sam_predictor=sam_predictor,
            text_prompts=DEBUG_PROMPTS,
            save_path=str(save_path)
        )

        print(f"✅ {img_path.name}: {len(detections)} objects")