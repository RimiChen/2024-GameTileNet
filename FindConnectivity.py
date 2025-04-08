import os
import cv2
import numpy as np
import json
from skimage.metrics import structural_similarity as ssim

# Configuration - Change these paths as needed
TILESET_FOLDER = "Data/GameTile/small_Tilesets"  # Folder containing original tileset images
SPLIT_TILE_FOLDER = "Data/GameTile/small_dataset"  # Folder containing split tiles in subdirectories
TILE_SIZE = 32  # Tile size (32x32 pixels)
THRESHOLD = 0.85  # SSIM threshold for connectivity
TRANSPARENCY_THRESHOLD = 0.9  # If more than 90% of the edge is transparent, it's not linked

# Get list of tileset images
tileset_images = [f for f in os.listdir(TILESET_FOLDER) if f.endswith(".png")]

# Function to check if an edge is mostly transparent
# def is_edge_transparent(edge):
#     if edge.shape[-1] == 4:  # Check if the image has an alpha channel
#         alpha_channel = edge[:, :, 3]
#         transparent_ratio = np.sum(alpha_channel == 0) / len(alpha_channel)
#         return transparent_ratio > TRANSPARENCY_THRESHOLD
#     return False  # Assume no transparency if no alpha channel
def is_edge_transparent(edge):
    if edge.ndim == 3 and edge.shape[-1] == 4:  # Check if image has 4 channels (RGBA)
        alpha_channel = edge[:, :, 3]
        transparent_ratio = np.sum(alpha_channel == 0) / alpha_channel.size
        return transparent_ratio > TRANSPARENCY_THRESHOLD
    return False  # Assume non-transparent if no alpha channel


# Function to load a tile
def load_tile(tileset_id, x, y):
    tile_path = os.path.join(SPLIT_TILE_FOLDER, tileset_id, f"tiles_{x}_{y}.png")
    if os.path.exists(tile_path):
        return cv2.imread(tile_path, cv2.IMREAD_UNCHANGED)
    return None


def mse(imageA, imageB):
    """Compute the Mean Squared Error between two images."""
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return 1 - (err / 255.0)  # Normalize to a similarity range (0-1)

def compare_edges(tile1, tile2, direction):
    if tile1 is None or tile2 is None:
        return 0  # No similarity if one tile is missing

    # Extract edges for comparison
    if direction in ["right_top", "right_down"]:
        edge1 = tile1[: TILE_SIZE // 2, -1] if "top" in direction else tile1[TILE_SIZE // 2 :, -1]
        edge2 = tile2[: TILE_SIZE // 2, 0] if "top" in direction else tile2[TILE_SIZE // 2 :, 0]
    elif direction in ["left_top", "left_down"]:
        edge1 = tile1[: TILE_SIZE // 2, 0] if "top" in direction else tile1[TILE_SIZE // 2 :, 0]
        edge2 = tile2[: TILE_SIZE // 2, -1] if "top" in direction else tile2[: TILE_SIZE // 2, -1]
    elif direction in ["top_left", "top_right"]:
        edge1 = tile1[0, : TILE_SIZE // 2] if "left" in direction else tile1[0, TILE_SIZE // 2 :]
        edge2 = tile2[-1, : TILE_SIZE // 2] if "left" in direction else tile2[-1, TILE_SIZE // 2 :]
    elif direction in ["down_left", "down_right"]:
        edge1 = tile1[-1, : TILE_SIZE // 2] if "left" in direction else tile1[-1, TILE_SIZE // 2 :]
        edge2 = tile2[0, : TILE_SIZE // 2] if "left" in direction else tile2[0, TILE_SIZE // 2 :]
    else:
        return 0

    # Check transparency
    if is_edge_transparent(edge1) or is_edge_transparent(edge2):
        return 0  # Considered not linked if mostly transparent

    # Convert to grayscale
    edge1_gray = cv2.cvtColor(np.expand_dims(edge1, axis=0), cv2.COLOR_BGR2GRAY)
    edge2_gray = cv2.cvtColor(np.expand_dims(edge2, axis=0), cv2.COLOR_BGR2GRAY)

    # Determine the max window size that fits in the image
    min_dim = min(edge1_gray.shape[0], edge1_gray.shape[1])
    win_size = min(7, min_dim)  # Ensure win_size is at most 7
    if win_size % 2 == 0:  # SSIM requires odd win_size
        win_size -= 1  

    # If the edge is still too small for SSIM, fall back to MSE
    if win_size < 3:
        return mse(edge1_gray, edge2_gray)

    # Compute Structural Similarity Index (SSIM)
    similarity = ssim(edge1_gray, edge2_gray, win_size=win_size, channel_axis=None)
    return similarity



# Analyze connectivity
results = []

for tileset in tileset_images:
    tileset_id = os.path.splitext(tileset)[0]  # Extract ID from filename (e.g., "000_001")

    # Get the number of tiles by checking the folder
    tileset_folder = os.path.join(SPLIT_TILE_FOLDER, tileset_id)
    if not os.path.exists(tileset_folder):
        continue

    # Detect tile grid size dynamically
    tile_files = [f for f in os.listdir(tileset_folder) if f.startswith("tiles_") and f.endswith(".png")]
    tile_coords = [(int(f.split("_")[1]), int(f.split("_")[2].split(".")[0])) for f in tile_files]
    if not tile_coords:
        continue

    max_x = max(coord[0] for coord in tile_coords) + 1
    max_y = max(coord[1] for coord in tile_coords) + 1

    for x, y in tile_coords:
        tile = load_tile(tileset_id, x, y)
        connections = {"tileset": tileset_id, "tile_x": x, "tile_y": y}

        # Define neighbor checks
        neighbors = {
            "right_top": (x + 1, y) if x + 1 < max_x else None,
            "right_down": (x + 1, y) if x + 1 < max_x else None,
            "left_top": (x - 1, y) if x - 1 >= 0 else None,
            "left_down": (x - 1, y) if x - 1 >= 0 else None,
            "top_left": (x, y - 1) if y - 1 >= 0 else None,
            "top_right": (x, y - 1) if y - 1 >= 0 else None,
            "down_left": (x, y + 1) if y + 1 < max_y else None,
            "down_right": (x, y + 1) if y + 1 < max_y else None,
        }

        # Check connectivity for all 8 directions
        for direction, neighbor in neighbors.items():
            if neighbor:
                neighbor_tile = load_tile(tileset_id, neighbor[0], neighbor[1])
                connections[direction] = compare_edges(tile, neighbor_tile, direction) > THRESHOLD
            else:
                connections[direction] = False

        results.append(connections)

# Save results as JSON
output_file = "tile_connectivity_analysis.json"
with open(output_file, "w") as json_file:
    ### Convert NumPy boolean values (numpy.bool_) to regular Python booleans (bool) before saving the
    json.dump(results, json_file, indent=4, default=lambda x: bool(x) if isinstance(x, np.bool_) else x)

print(f"Connectivity analysis saved to {output_file}")