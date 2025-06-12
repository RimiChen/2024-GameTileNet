import torch
import numpy as np
import cv2
import os
from PIL import Image
from yolov5 import YOLOv5
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import json

tileset_folder = "Data/GameTile/small_Segmenets_model/001_005/"
tileset_name = "001_001.png"
tile_size = 32
out_folder = "Data/GameTile/small_Segmenets_complete/"

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
    return output_path

def is_object_complete(cropped_image_path, model):
    # Load cropped image
    image = cv2.imread(cropped_image_path)
    if image is None:
        return False
    
    # Perform object detection
    results = model.predict(image)
    
    # Check if the detected objects are close to the edges
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = det
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        image_height, image_width, _ = image.shape

        # If the bounding box is close to the edges, consider it incomplete
        if x1 < 10 or y1 < 10 or x2 > (image_width - 10) or y2 > (image_height - 10):
            return False

    return True

def segment_and_save_objects(image_path, output_dir, model, model_type='vit_h'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    results = []
    
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    # Load SAM model
    sam_checkpoint_path = chkpt_path_2  # Replace with the actual path to your SAM checkpoint file
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
    sam.to(device='cuda' if torch.cuda.is_available() else 'cpu')

    # Prepare the image for segmentation
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tensor = torch.from_numpy(np.array(image_pil)).permute(2, 0, 1).unsqueeze(0).float()

    # Generate masks
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image_rgb)

    # Process each mask
    for i, mask in enumerate(masks):
        x, y, w, h = cv2.boundingRect(mask['segmentation'].astype(np.uint8))
        adjusted_box = adjust_bounding_box((x, y, w, h))
        cropped_image_path = save_cropped_image(image, adjusted_box, output_dir, i)

        # Check if the object is complete
        is_complete = is_object_complete(cropped_image_path, model)
        
        result = {
            'image': cropped_image_path,
            'bbox': [x, y, w, h],
            'is_complete': is_complete
        }
        results.append(result)
    
    return results

def process_tileset_images(input_folder, output_base_dir, yolo_model, model_type='vit_h', tile_size=32):
    all_results = {}
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            image_path = os.path.join(input_folder, filename)
            tileset_name = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_base_dir, tileset_name)
            results = segment_and_save_objects(image_path, output_dir, yolo_model, model_type)
            all_results[tileset_name] = results

    # Save all results to a JSON file
    output_json_path = os.path.join(output_base_dir, 'segmentation_results.json')
    with open(output_json_path, 'w') as f:
        json.dump(all_results, f, indent=4)

# Example usage
input_folder = tileset_folder  # Replace with your input folder path containing tileset images
output_base_dir = out_folder  # Base directory to save the cropped images

# Load YOLOv5 model
yolo_model = YOLOv5("yolov5s.pt")  # Using the small version of YOLOv5

process_tileset_images(input_folder, output_base_dir, yolo_model)