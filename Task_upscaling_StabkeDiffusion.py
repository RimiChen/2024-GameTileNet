import os
from PIL import Image
from diffusers import StableDiffusionUpscalePipeline
import torch

# -------- Configuration --------
# input_root = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"  # path to original tile images (subfolders inside)
# output_root = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/sd_fidelity"  # where upscaled results go
# input_root = "Data/GameTile/complete_labels_output_model/complete"  # e.g., input_tiles/folder_x/*.png
# output_root= "Data/GameTile/complete_labels_output_model/upscaled_tiles/sd_fidelity"
input_root = "Data/GameTile/complete_author_cleaned"  # e.g., input_tiles/folder_x/*.png
output_root= "Data/GameTile/complete_author_processed/sd_fidelity"
model_id = "stabilityai/stable-diffusion-x4-upscaler"
prompt = "a pixel art game tile, fantasy style"

# -------- Background fill helper --------
def paste_on_background(img, color=(255, 255, 255)):
    bg = Image.new("RGB", img.size, color)
    if img.mode == "RGBA":
        bg.paste(img, mask=img.split()[3])  # use alpha
    else:
        bg.paste(img)
    return bg

# -------- Load pipeline --------
pipe = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# -------- Process tiles --------
for folder in os.listdir(input_root):
    folder_path = os.path.join(input_root, folder)
    if not os.path.isdir(folder_path):
        continue

    out_folder = os.path.join(output_root, folder)
    os.makedirs(out_folder, exist_ok=True)

    for file in os.listdir(folder_path):
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        image_path = os.path.join(folder_path, file)
        img = Image.open(image_path).convert("RGBA").resize((128, 128))
        img_with_bg = paste_on_background(img, color=(255, 255, 255))  # change to (0,0,0) for black bg

        upscaled = pipe(prompt=prompt, image=img_with_bg).images[0]
        upscaled.save(os.path.join(out_folder, file))
        print(f"Upscaled: {file}")