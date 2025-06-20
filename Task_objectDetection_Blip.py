import os
import json
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# === Settings ===
# ROOT_FOLDER = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/bicubic"  # This folder contains subfolders with images
ROOT_FOLDER = "Data/GameTile/complete_author_cleaned"  # This folder contains subfolders with images
OUTPUT_JSON = "Data/GameTile/vlm_caption_results_author_original.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# === Load Model ===
print("🔧 Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(DEVICE)

# === Gather all image paths recursively ===
def gather_images_recursively(folder, exts={".png", ".jpg", ".jpeg"}):
    image_paths = []
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                image_paths.append(os.path.join(root, f))
    return image_paths

image_paths = gather_images_recursively(ROOT_FOLDER)
print(f"📷 Found {len(image_paths)} images.")
if not image_paths:
    print("❌ No images found. Please check your path:", ROOT_FOLDER)
    exit()

# === Generate Captions ===
captions = []
for img_path in image_paths:
    try:
        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        print(f"📝 {os.path.basename(img_path)}: {caption}")
        captions.append({"image": img_path, "caption": caption})
    except Exception as e:
        print(f"⚠️ Failed to process {img_path}: {e}")

# === Save Results ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(captions, f, indent=2, ensure_ascii=False)
print(f"\n🎯 All results saved to: {OUTPUT_JSON}")
