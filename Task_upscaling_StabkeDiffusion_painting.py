import os
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
import keyboard

# -------- Configuration --------
# input_root = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"  # path to original tile images (subfolders inside)
# output_root = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/sd_img2img"  # where upscaled results go
# input_root = "Data/GameTile/complete_labels_output_model/complete"  # e.g., input_tiles/folder_x/*.png
# output_root= "Data/GameTile/complete_labels_output_model/upscaled_tiles/sd_img2img"
input_root = "Data/GameTile/complete_author_cleaned"  # e.g., input_tiles/folder_x/*.png
output_root= "Data/GameTile/complete_author_processed/sd_img2img"
# import os
# from PIL import Image
# import torch
# from diffusers import StableDiffusionImg2ImgPipeline
# import keyboard

# # -------- Configuration --------
# input_root = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"
# output_root = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/sd_img2img"
prompt = "refined, high-resolution rendering of the same top-down pixel-art game tile, preserving the object, layout, and semantics, with clean outlines and vivid color" # the safe prompt for first version
strength = 0.3
guidance_scale = 7.5
resize_input = (512, 512)

# -------- Load Stable Diffusion Pipeline --------
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    safety_checker=None  # Disable safety checker to avoid black images
).to("cuda")

# -------- Transparent background handling --------
def paste_on_background(img, color=(255, 255, 255)):
    bg = Image.new("RGB", img.size, color)
    if img.mode == "RGBA":
        bg.paste(img, mask=img.split()[3])
    else:
        bg.paste(img)
    return bg

# -------- Image Processing Loop --------
for folder in os.listdir(input_root):
    folder_path = os.path.join(input_root, folder)
    if not os.path.isdir(folder_path):
        continue

    out_folder = os.path.join(output_root, folder)
    os.makedirs(out_folder, exist_ok=True)

    for file in os.listdir(folder_path):
        if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        image_path = os.path.join(folder_path, file)
        img = Image.open(image_path).convert("RGBA")
        img = paste_on_background(img, color=(255, 255, 255))
        img = img.resize(resize_input)

        result = pipe(
            prompt=prompt,
            image=img,
            strength=strength,
            guidance_scale=guidance_scale,
        ).images[0]

        # Check if the result is black (due to NSFW filter)
        if not result.getbbox():
            print(f"⚠️ Skipped {file}: generated image is empty/black.")
            result = img  # fallback to original

        result.save(os.path.join(out_folder, file))
        print(f"✅ Generated tile: {file}")

        if keyboard.is_pressed("q"):
            print("⛔ Execution stopped by user (pressed 'q').")
            raise SystemExit
