import cv2
import numpy as np
import os


tileset_folder = "Data/GameTile/small_Tilesets/"
tileset_name = "001_001.png"
tile_size = 32
out_folder = "Data/GameTile/small_Segmenets/"


import cv2
import numpy as np
import os

def adjust_bounding_box(box, step=32):
    x, y, w, h = box
    x = (x // step) * step
    y = (y // step) * step
    w = ((w + step - 1) // step) * step
    h = ((h + step - 1) // step) * step
    return x, y, w, h

def save_cropped_image(image, box, output_dir):
    x, y, w, h = box
    cropped_image = image[y:y+h, x:x+w]
    output_path = os.path.join(output_dir, f'object_{x}_{y}_{w}_{h}.png')
    cv2.imwrite(output_path, cropped_image)

def extract_objects(image_path, output_base_dir):
    # Extract tileset name from image path
    tileset_name = os.path.splitext(os.path.basename(image_path))[0]
    output_dir = os.path.join(output_base_dir, f'out_{tileset_name}')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Check if the image is loaded successfully
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    # Apply binary threshold
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through contours and create bounding boxes
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        adjusted_box = adjust_bounding_box((x, y, w, h))
        save_cropped_image(image, adjusted_box, output_dir)

def process_tileset_images(input_folder, output_base_dir):
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            image_path = os.path.join(input_folder, filename)
            extract_objects(image_path, output_base_dir)

# Example usage
input_folder =  tileset_folder  # Replace with your input folder path containing tileset images
output_base_dir = out_folder  # Base directory to save the cropped images
process_tileset_images(input_folder, output_base_dir)