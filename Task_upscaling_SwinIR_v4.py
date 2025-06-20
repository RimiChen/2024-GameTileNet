import os
import cv2
import numpy as np
from PIL import Image, ImageOps
import torch
from basicsr.archs.swinir_arch import SwinIR

# --- Configuration ---
input_root = 'Data/GameTile/complete_labels_output_model/complete'
output_root = 'Data/GameTile/complete_labels_output_model/upscaled_tiles/swinir_x4'
model_path = 'Data/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN-with-dict-keys-params-and-params_ema.pth'
# 'experiments/pretrained_models/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_PSNR.pth'
SCALE = 4
MIN_SIZE = 64
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# --- Prepare model ---
print('🔧 Loading SwinIR model...')
model = SwinIR(
    upscale=SCALE,
    in_chans=3,
    img_size=64,
    window_size=8,
    img_range=1.0,
    depths=[6, 6, 6, 6, 6, 6],
    embed_dim=180,
    num_heads=[6, 6, 6, 6, 6, 6],
    mlp_ratio=2,
    # upsampler='pixelshuffle',
    upsampler = 'nearest+conv',    
    resi_connection='1conv'
).to(DEVICE)

pretrained_state = torch.load(model_path)
if 'params_ema' in pretrained_state:
    pretrained_state = pretrained_state['params_ema']
model.load_state_dict(pretrained_state, strict=True)
model.eval()

# --- Padding function using white background ---
def pad_to_min_size(pil_img, min_size=MIN_SIZE):
    if pil_img.width < min_size or pil_img.height < min_size:
        delta_w = max(0, min_size - pil_img.width)
        delta_h = max(0, min_size - pil_img.height)
        padding = (delta_w // 2, delta_h // 2, delta_w - delta_w // 2, delta_h - delta_h // 2)
        pil_img = ImageOps.expand(pil_img, padding, fill=(255, 255, 255))
    return pil_img

# --- Upscaling function ---
def upscale_image(img):
    img = img.astype(np.float32) / 255.0
    img = torch.from_numpy(np.transpose(img, (2, 0, 1))).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        output = model(img).data.squeeze().float().cpu().clamp_(0, 1).numpy()
    output = np.transpose(output, (1, 2, 0)) * 255.0
    return np.round(output).astype(np.uint8)

# --- Main loop ---
error_log = {}
total_images = 0
processed_images = 0

for subdir, _, files in os.walk(input_root):
    for file in files:
        if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        total_images += 1
        input_path = os.path.join(subdir, file)
        rel_path = os.path.relpath(input_path, input_root)
        output_path = os.path.join(output_root, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            pil_img = Image.open(input_path).convert("RGBA")
            white_bg = Image.new("RGBA", pil_img.size, (255, 255, 255, 255))
            composite = Image.alpha_composite(white_bg, pil_img).convert("RGB")
            composite = pad_to_min_size(composite)
            img = np.array(composite)
            upscaled = upscale_image(img)
            cv2.imwrite(output_path, cv2.cvtColor(upscaled, cv2.COLOR_RGB2BGR))
            processed_images += 1
        except Exception as e:
            error_log[input_path] = str(e)

# --- Save error log if needed ---
if error_log:
    import json
    with open('swinir_error_log_padded.json', 'w') as f:
        json.dump(error_log, f, indent=2)

print(f"✅ Finished processing: {processed_images}/{total_images} images")
if error_log:
    print(f"⚠️ {len(error_log)} images failed. See 'swinir_error_log_padded.json'")
