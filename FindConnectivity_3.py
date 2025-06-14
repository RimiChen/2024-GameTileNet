import os
import cv2
import numpy as np
import json
from skimage.metrics import structural_similarity as ssim

# Configuration
TILESET_FOLDER = "Data/GameTile/small_Tilesets"
SPLIT_TILE_FOLDER = "Data/GameTile/small_dataset/Tiles/"
OUTPUT_FOLDER = "Data/GameTile/connectivity_results_4"  # Folder to store JSON files
TILE_SIZE = 32
THRESHOLD = 0.55
TRANSPARENCY_THRESHOLD = 0.6  # Transparency detection threshold
EDGE_CHECK_ROWS = 4  # Number of pixels to check at the edge

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Get list of tileset images
tileset_images = [f for f in os.listdir(TILESET_FOLDER) if f.endswith(".png")]

# Function to check if an edge section is mostly transparent
def is_edge_section_transparent(edge):
    if edge.ndim == 3 and edge.shape[-1] == 4:  # Check if RGBA image
        alpha_channel = edge[:, :, 3]
        transparent_ratio = np.sum(alpha_channel == 0) / alpha_channel.size
        return transparent_ratio > TRANSPARENCY_THRESHOLD  # True if mostly transparent
    return False  # Assume not transparent if no alpha channel

# Function to check transparency for all eight half-edges of a tile
def check_edge_transparency(tile):
    return {
        "top_left": is_edge_section_transparent(tile[0: TILE_SIZE // 2, 0:EDGE_CHECK_ROWS]),
        "top_right": is_edge_section_transparent(tile[TILE_SIZE // 2: TILE_SIZE, 0:EDGE_CHECK_ROWS]),
        "down_left": is_edge_section_transparent(tile[0: TILE_SIZE // 2, TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE]),
        "down_right": is_edge_section_transparent(tile[TILE_SIZE // 2: TILE_SIZE, TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE]),
        "left_top": is_edge_section_transparent(tile[0:EDGE_CHECK_ROWS, 0: TILE_SIZE // 2]),
        "left_down": is_edge_section_transparent(tile[0:EDGE_CHECK_ROWS, TILE_SIZE // 2: TILE_SIZE]),
        "right_top": is_edge_section_transparent(tile[TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE, 0: TILE_SIZE // 2]),
        "right_down": is_edge_section_transparent(tile[TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE, TILE_SIZE // 2: TILE_SIZE])
    }

# Function to load a tile
def load_tile(tileset_id, x, y):
    tile_path = os.path.join(SPLIT_TILE_FOLDER, tileset_id, f"tiles_{x}_{y}.png")
    if os.path.exists(tile_path):
        return cv2.imread(tile_path, cv2.IMREAD_UNCHANGED)
    return None

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return 1 - (err / 255.0)

def compare_edges(tile1, tile2, direction):
    if tile1 is None or tile2 is None:
        return 0

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

    if is_edge_section_transparent(edge1) or is_edge_section_transparent(edge2):
        return 0

    edge1_gray = cv2.cvtColor(np.expand_dims(edge1, axis=0), cv2.COLOR_BGR2GRAY)
    edge2_gray = cv2.cvtColor(np.expand_dims(edge2, axis=0), cv2.COLOR_BGR2GRAY)

    min_dim = min(edge1_gray.shape[0], edge1_gray.shape[1])
    win_size = min(7, min_dim)
    if win_size % 2 == 0:
        win_size -= 1  

    if win_size < 3:
        return mse(edge1_gray, edge2_gray)

    similarity = ssim(edge1_gray, edge2_gray, win_size=win_size, channel_axis=None)
    return similarity

# Process each tileset separately
for tileset in tileset_images:
    tileset_id = os.path.splitext(tileset)[0]  # Extract ID (e.g., "000_001")

    tileset_folder = os.path.join(SPLIT_TILE_FOLDER, tileset_id)

    print(f"[INFO] Processing tileset: {tileset_id}")
    print(f"        -> tileset folder exists: {os.path.exists(tileset_folder)}")

    if not os.path.exists(tileset_folder):
        continue

    tile_files = [f for f in os.listdir(tileset_folder) if f.startswith("tiles_") and f.endswith(".png")]
    tile_coords = [(int(f.split("_")[1]), int(f.split("_")[2].split(".")[0])) for f in tile_files]
    print(f"        -> Found {len(tile_coords)} tiles in {tileset_folder}")

    if not tile_coords:
        continue

    max_x = max(coord[0] for coord in tile_coords) + 1
    max_y = max(coord[1] for coord in tile_coords) + 1

    results = []  # Store results for this tileset only

    for x, y in tile_coords:
        tile = load_tile(tileset_id, x, y)
        if tile is None:
            continue

        connectivity_list = []
        possible_connectivity_list = []
        edge_transparency = check_edge_transparency(tile)

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

        for direction, neighbor in neighbors.items():
            if neighbor:
                neighbor_tile = load_tile(tileset_id, neighbor[0], neighbor[1])
                if compare_edges(tile, neighbor_tile, direction) > THRESHOLD:
                    connectivity_list.append(direction)

            if not edge_transparency[direction]:
                possible_connectivity_list.append(direction)

        results.append({
            "tile_x": x,
            "tile_y": y,
            "connectivity": connectivity_list,
            "possible_connectivity": possible_connectivity_list,
            "edge_transparency": edge_transparency
        })

    # Save each tileset's result separately


    output_file = os.path.join(OUTPUT_FOLDER, f"tile_connectivity-{tileset_id}.json")
    print(f"[SAVE] Writing results to {output_file} with {len(results)} tiles.")
    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4, default=lambda x: bool(x) if isinstance(x, np.bool_) else x)

print("All tileset connectivity files saved.")
