import os
import cv2
import torch
import numpy as np
import json
from tqdm import tqdm
from basicsr.archs.swinir_arch import SwinIR
from realesrgan import RealESRGANer

# -------- Configuration --------
input_root = "Data/GameTile/complete_author_cleaned"
output_root = "Data/GameTile/complete_author_processed/swinir_x4"
model_path = "Data/001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth"
scale = 4
tile_size = 256

# -------- Load SwinIR Model --------
model = SwinIR(
    upscale=4,
    in_chans=3,
    img_size=64,
    window_size=8,
    img_range=1.0,
    depths=[6, 6, 6, 6, 6, 6],
    embed_dim=180,
    num_heads=[6, 6, 6, 6, 6, 6],
    mlp_ratio=2,
    upsampler='pixelshuffle',
    resi_connection='1conv'
)

upsampler = RealESRGANer(
    scale=scale,
    model_path=model_path,
    model=model,
    tile=tile_size,
    tile_pad=10,
    pre_pad=0,
    half=False
)

# -------- Process Folders --------
os.makedirs(output_root, exist_ok=True)
error_log = {}

for folder in os.listdir(input_root):
    subfolder_path = os.path.join(input_root, folder)
    if not os.path.isdir(subfolder_path):
        continue

    save_subfolder = os.path.join(output_root, folder)
    os.makedirs(save_subfolder, exist_ok=True)

    for img_name in tqdm(os.listdir(subfolder_path), desc=f'Processing {folder}'):
        if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        img_path = os.path.join(subfolder_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

        if img is None:
            error_log[img_path] = "cv2.imread failed (None returned)"
            continue

        try:
            # Handle alpha transparency (convert to white background)
            if img.shape[-1] == 4:
                b, g, r, a = cv2.split(img)
                alpha = a.astype(np.float32) / 255.0
                white_bg = np.ones_like(b, dtype=np.float32) * 255
                b = b * alpha + white_bg * (1 - alpha)
                g = g * alpha + white_bg * (1 - alpha)
                r = r * alpha + white_bg * (1 - alpha)
                img = cv2.merge([b, g, r]).astype(np.uint8)

            # Convert grayscale or other formats to 3-channel RGB
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            output, _ = upsampler.enhance(img, outscale=scale)
            save_path = os.path.join(save_subfolder, img_name)
            cv2.imwrite(save_path, output)

        except Exception as e:
            error_log[img_path] = f"Error during enhancement: {str(e)}"

# -------- Save error log --------
with open("swinir_upscale_error_log.json", "w") as f:
    json.dump(error_log, f, indent=2)

print(f"✅ Done. Errors recorded: {len(error_log)}")
