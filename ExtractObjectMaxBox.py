import torch
import numpy as np
import cv2
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import os

tileset_folder = "Data/GameTile/small_Tilesets/"
tileset_name = "001_001.png"
tile_size = 32
out_folder = "Data/GameTile/small_Segmenets_model_max/"

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

def merge_overlapping_boxes(boxes):
    if not boxes:
        return []
    
    # Sort the boxes by the x coordinate
    boxes = sorted(boxes, key=lambda box: box[0])
    
    merged_boxes = []
    current_box = boxes[0]
    
    for box in boxes[1:]:
        if (box[0] <= current_box[0] + current_box[2]) and (box[1] <= current_box[1] + current_box[3]):
            x = min(current_box[0], box[0])
            y = min(current_box[1], box[1])
            w = max(current_box[0] + current_box[2], box[0] + box[2]) - x
            h = max(current_box[1] + current_box[3], box[1] + box[3]) - y
            current_box = (x, y, w, h)
        else:
            merged_boxes.append(current_box)
            current_box = box
            
    merged_boxes.append(current_box)
    return merged_boxes

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
    image_tensor = torch.from_numpy(np.array(image_pil)).permute(2, 0, 1).unsqueeze(0)

    # Generate masks
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image_rgb)  # Pass the numpy array directly

    # Extract bounding boxes
    boxes = []
    for mask in masks:
        x, y, w, h = cv2.boundingRect(mask['segmentation'].astype(np.uint8))
        adjusted_box = adjust_bounding_box((x, y, w, h))
        boxes.append(adjusted_box)

    # Merge overlapping boxes
    merged_boxes = merge_overlapping_boxes(boxes)

    # Save cropped images
    for i, box in enumerate(merged_boxes):
        save_cropped_image(image, box, output_dir, i)

def process_tileset_images(input_folder, output_base_dir, model_type='vit_h'):
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            image_path = os.path.join(input_folder, filename)
            tileset_name = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_base_dir, tileset_name)
            segment_and_save_objects(image_path, output_dir, model_type)

# Example usage
input_folder = tileset_folder  # Replace with your input folder path containing tileset images
output_base_dir = out_folder  # Base directory to save the cropped images
model_type = 'vit_h'  # Specify the model type
process_tileset_images(input_folder, output_base_dir, model_type)