import torch
import numpy as np
import cv2
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import os


tileset_folder = "Data/GameTile/small_Tilesets/"
tileset_name = "001_001.png"
tile_size = 32
out_folder = "Data/GameTile/small_Segmenets_model/"

from huggingface_hub import hf_hub_download

chkpt_path = hf_hub_download("ybelkada/segment-anything", "checkpoints/sam_vit_b_01ec64.pth")
chkpt_path_2 = "Data/sam_vit_h_4b8939.pth" 


def adjust_bounding_box(box, step=32):
    x, y, w, h = box
    x = (x // step) * step
    y = (y // step) * step
    w = ((w + step - 1) // step) * step
    h = ((h + step - 1) // step) * step
    return x, y, w, h

def save_cropped_image(image, box, output_dir, index):
    x, y, w, h = box
    cropped_image = image[y:y+h, x:x+w]
    output_path = os.path.join(output_dir, f'object_{x}_{y}_{w}_{h}_{index}.png')
    cv2.imwrite(output_path, cropped_image)

def segment_and_save_objects(image_path, output_dir, model_type='vit_h'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    # Load SAM model
    sam_checkpoint_path = chkpt_path_2  # Replace with the actual path to your SAM checkpoint file
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
    sam.to(device='cuda' if torch.cuda.is_available() else 'cpu')

    # Prepare the image for SAM
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tensor = torch.from_numpy(np.array(image_pil)).permute(2, 0, 1).unsqueeze(0).float()

    # Generate masks
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image_rgb)  # Updated to pass the numpy array directly

    # Process each mask
    for i, mask in enumerate(masks):
        x, y, w, h = cv2.boundingRect(mask['segmentation'].astype(np.uint8))
        adjusted_box = adjust_bounding_box((x, y, w, h))
        save_cropped_image(image, adjusted_box, output_dir, i)

def process_tileset_images(input_folder, output_base_dir, model_type='vit_h', tile_size=32):
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            image_path = os.path.join(input_folder, filename)
            tileset_name = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_base_dir, tileset_name)
            segment_and_save_objects(image_path, output_dir, model_type)


# Example usage
image_path = tileset_folder  # Replace with your image path
output_dir = out_folder  # Directory to save the cropped images
segment_and_save_objects(image_path, output_dir)

# Example usage
input_folder = tileset_folder # Replace with your input folder path containing tileset images
output_base_dir = out_folder  # Base directory to save the cropped images
model_type = 'vit_h'  # Specify the model type
process_tileset_images(input_folder, output_base_dir, model_type)