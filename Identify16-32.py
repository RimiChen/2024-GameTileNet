import cv2
import numpy as np

tileset_folder = "Data/GameTile/16/"
tileset_name = "001_001.png"

def is_tileset_32_or_16_based(image_path):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Check if the image is loaded successfully
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return None

    # Apply edge detection
    edges = cv2.Canny(image, 50, 150)

    # Sum the edge pixels along the vertical and horizontal axes
    vertical_sum = np.sum(edges, axis=0)
    horizontal_sum = np.sum(edges, axis=1)

    # Find the peaks in the sums to identify the tile edges
    vertical_peaks = np.where(vertical_sum > vertical_sum.mean())[0]
    horizontal_peaks = np.where(horizontal_sum > horizontal_sum.mean())[0]

    # Calculate the distances between consecutive peaks
    vertical_diffs = np.diff(vertical_peaks)
    horizontal_diffs = np.diff(horizontal_peaks)

    # Count the occurrences of 16 and 32 distances
    vertical_counts = {16: 0, 32: 0}
    horizontal_counts = {16: 0, 32: 0}

    for diff in vertical_diffs:
        if diff in vertical_counts:
            vertical_counts[diff] += 1

    for diff in horizontal_diffs:
        if diff in horizontal_counts:
            horizontal_counts[diff] += 1

    # Determine if the tileset is 32-based or 16-based
    is_32_based = (vertical_counts[32] > vertical_counts[16]) and (horizontal_counts[32] > horizontal_counts[16])
    is_16_based = (vertical_counts[16] > vertical_counts[32]) and (horizontal_counts[16] > horizontal_counts[32])

    if is_32_based:
        return 32
    elif is_16_based:
        return 16
    else:
        return None

# Example usage
image_path = tileset_folder +tileset_name    # Replace with your image path
tile_size = is_tileset_32_or_16_based(image_path)
if tile_size:
    print(f"The tileset is {tile_size}-based.")
else:
    print("Could not determine the tile size.")