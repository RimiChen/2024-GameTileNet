import os
import cv2
import torch
import numpy as np
from tqdm import tqdm
from basicsr.archs.swinir_arch import SwinIR
from realesrgan import RealESRGANer

# -------- Configuration --------
# input_root = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"  # path to original tile images (subfolders inside)
# output_root = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/swinir_x4"  # where upscaled results go
# input_root = "Data/GameTile/complete_labels_output_model/complete"  # e.g., input_tiles/folder_x/*.png
# output_root= "Data/GameTile/complete_labels_output_model/upscaled_tiles/swinir_x4"
input_root = "Data/GameTile/complete_author_cleaned"  # e.g., input_tiles/folder_x/*.png
output_root= "Data/GameTile/complete_author_processed/swinir_x4"
model_path = "Data/001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth"  # corrected model checkpoint path
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
    upsampler='pixelshuffle',         # <-- Fix here
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

        try:
            output, _ = upsampler.enhance(img, outscale=scale)
            cv2.imwrite(os.path.join(save_subfolder, img_name), output)
        except Exception as e:
            print(f"[ERROR] Failed {img_name}: {e}")
