import os
import numpy as np
from PIL import Image
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

# --------- Settings ---------
# INPUT_DIR = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"  # e.g., input_tiles/folder_x/*.png
# OUTPUT_DIR = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/realesrgan_x4"
# INPUT_DIR = "Data/GameTile/complete_labels_output_model/complete"  # e.g., input_tiles/folder_x/*.png
# OUTPUT_DIR = "Data/GameTile/complete_labels_output_model/upscaled_tiles/realesrgan_x4"
INPUT_DIR  = "Data/GameTile/complete_author_cleaned"  # e.g., input_tiles/folder_x/*.png
OUTPUT_DIR= "Data/GameTile/complete_author_processed/realesrgan_x4"
# INPUT_DIR = 'input_tiles'
# OUTPUT_DIR = 'upscaled_tiles/realesrgan_x4'
MODEL_PATH = 'Data/weights/RealESRGAN_x4plus.pth'
UPSCALE = 4
FILL_BACKGROUND = True
BACKGROUND_COLOR = (255, 255, 255)
# ----------------------------

def fill_transparency(img, color=(255, 255, 255)):
    if img.mode == 'RGBA':
        bg = Image.new("RGB", img.size, color)
        bg.paste(img, mask=img.split()[3])
        return bg
    elif img.mode != 'RGB':
        return img.convert("RGB")
    return img

# Load ESRGAN model
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23,
                num_grow_ch=32, scale=UPSCALE)
upscaler = RealESRGANer(
    scale=UPSCALE,
    model_path=MODEL_PATH,
    model=model,
    tile=0,
    tile_pad=10,
    pre_pad=0,
    half=False,
    gpu_id=0 if torch.cuda.is_available() else None
)

# Upscale loop
for root, _, files in os.walk(INPUT_DIR):
    for fname in files:
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        in_path = os.path.join(root, fname)
        rel_path = os.path.relpath(in_path, INPUT_DIR)
        out_path = os.path.join(OUTPUT_DIR, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        try:
            img = Image.open(in_path)
            img = fill_transparency(img, BACKGROUND_COLOR)
            img_np = np.array(img)
            output, _ = upscaler.enhance(img_np, outscale=UPSCALE)
            Image.fromarray(output).save(out_path)
            print(f"[SAVE] {out_path}")
        except Exception as e:
            print(f"[ERROR] {in_path}: {e}")


