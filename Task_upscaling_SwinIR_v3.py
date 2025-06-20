import os
import cv2
import torch
import json
import numpy as np
from PIL import Image
from basicsr.archs.swinir_arch import SwinIR
from torchvision.transforms.functional import to_tensor, to_pil_image

# ---- Configs ----
INPUT_FOLDER = "Data/GameTile/complete_author_cleaned"
OUTPUT_FOLDER = "Data/GameTile/complete_author_processed/swinir_x4"
LOG_PATH = "Data/GameTile/swinir_debug_cleaned_log.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MIN_SIZE = 64  # minimum resolution SwinIR accepts

# ---- Model ----
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
    upsampler="nearest+conv",
    resi_connection="1conv",
).to(DEVICE)

model_path = "Data/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN-with-dict-keys-params-and-params_ema.pth"
state_dict = torch.load(model_path)

# Fix: load from the 'params_ema' field if available
if "params_ema" in state_dict:
    state_dict = state_dict["params_ema"]

model.load_state_dict(state_dict, strict=True)
model.eval()

# ---- Ensure output folder exists ----
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

fail_log = {}


def center_pad_image(img, target_size=(64, 64), background=(255, 255, 255)):
    """
    Pads the input PIL image to the target size with center alignment and white background.
    If image is already larger, it will not be resized.
    """
    from PIL import Image

    if img.mode in ("RGBA", "LA"):
        # Convert transparent background to white
        background_img = Image.new("RGB", img.size, background)
        img = Image.alpha_composite(background_img.convert("RGBA"), img.convert("RGBA")).convert("RGB")
    else:
        img = img.convert("RGB")

    padded_img = Image.new("RGB", target_size, background)
    offset = ((target_size[0] - img.width) // 2, (target_size[1] - img.height) // 2)
    padded_img.paste(img, offset)
    return padded_img



def pad_if_needed(img, target_size=MIN_SIZE):
    h, w = img.shape[:2]
    pad_h = max(0, target_size - h)
    pad_w = max(0, target_size - w)
    if pad_h > 0 or pad_w > 0:
        img = cv2.copyMakeBorder(img, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)
    return img

def process_image(img_path, save_path):
    try:
        # img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

        img = Image.open(img_path).convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])  # Use alpha as mask
        img = np.array(bg)

        if img is None:
            raise ValueError("Unreadable or None image.")

        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            alpha = img[:, :, 3] / 255.0
            bg = np.ones_like(img[:, :, :3], dtype=np.uint8) * 255
            img = (alpha[:, :, None] * img[:, :, :3] + (1 - alpha[:, :, None]) * bg).astype(np.uint8)
        elif img.shape[2] != 3:
            raise ValueError(f"Invalid channel count: {img.shape[2]}")

        img = pad_if_needed(img)
        img_tensor = to_tensor(img).unsqueeze(0).to(DEVICE)
        img_tensor = img_tensor.type(torch.float32)

        with torch.no_grad():
            output = model(img_tensor).clamp_(0, 1)

        result = to_pil_image(output.squeeze().cpu())
        result.save(save_path)

    except Exception as e:
        fail_log[img_path] = str(e)

# ---- Walk through input folders ----
for subdir, _, files in os.walk(INPUT_FOLDER):
    rel_dir = os.path.relpath(subdir, INPUT_FOLDER)
    out_dir = os.path.join(OUTPUT_FOLDER, rel_dir)
    os.makedirs(out_dir, exist_ok=True)

    for fname in files:
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue
        src_path = os.path.join(subdir, fname)
        dst_path = os.path.join(out_dir, fname)
        process_image(src_path, dst_path)

# ---- Save error log ----
with open(LOG_PATH, "w") as f:
    json.dump(fail_log, f, indent=2)

print(f"✅ Finished. Processed images saved to {OUTPUT_FOLDER}")
print(f"⚠️ Failed images logged to {LOG_PATH} ({len(fail_log)} failures)")
