import os
import cv2
import numpy as np
import json
from skimage.metrics import structural_similarity as ssim

# === Configurable Parameters ===
TILESET_FOLDER = "Data/GameTile/small_Tilesets"
SPLIT_TILE_FOLDER = "Data/GameTile/small_dataset/Tiles"
OUTPUT_FOLDER = "Data/GameTile/connectivity_results_smart"

TILE_SIZE = 32
SSIM_THRESHOLD = 0.6                 # Smart rule: lower than conservative 0.85
TRANSPARENCY_THRESHOLD = 0.6        # Keep consistent with your best result
EDGE_CHECK_ROWS = 4

# === Ensure output directory exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Helper Functions ===
def is_edge_section_transparent(edge):
    if edge.ndim == 3 and edge.shape[-1] == 4:
        alpha_channel = edge[:, :, 3]
        transparent_ratio = np.sum(alpha_channel == 0) / alpha_channel.size
        return transparent_ratio > TRANSPARENCY_THRESHOLD
    return False

def check_edge_transparency(tile):
    return {
        "top_left": is_edge_section_transparent(tile[0:TILE_SIZE // 2, 0:EDGE_CHECK_ROWS]),
        "top_right": is_edge_section_transparent(tile[TILE_SIZE // 2:TILE_SIZE, 0:EDGE_CHECK_ROWS]),
        "down_left": is_edge_section_transparent(tile[0:TILE_SIZE // 2, TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE]),
        "down_right": is_edge_section_transparent(tile[TILE_SIZE // 2:TILE_SIZE, TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE]),
        "left_top": is_edge_section_transparent(tile[0:EDGE_CHECK_ROWS, 0:TILE_SIZE // 2]),
        "left_down": is_edge_section_transparent(tile[0:EDGE_CHECK_ROWS, TILE_SIZE // 2:TILE_SIZE]),
        "right_top": is_edge_section_transparent(tile[TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE, 0:TILE_SIZE // 2]),
        "right_down": is_edge_section_transparent(tile[TILE_SIZE - EDGE_CHECK_ROWS:TILE_SIZE, TILE_SIZE // 2:TILE_SIZE])
    }

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
        edge1 = tile1[:TILE_SIZE // 2, -1] if "top" in direction else tile1[TILE_SIZE // 2:, -1]
        edge2 = tile2[:TILE_SIZE // 2, 0] if "top" in direction else tile2[TILE_SIZE // 2:, 0]
    elif direction in ["left_top", "left_down"]:
        edge1 = tile1[:TILE_SIZE // 2, 0] if "top" in direction else tile1[TILE_SIZE // 2:, 0]
        edge2 = tile2[:TILE_SIZE // 2, -1] if "top" in direction else tile2[:TILE_SIZE // 2, -1]
    elif direction in ["top_left", "top_right"]:
        edge1 = tile1[0, :TILE_SIZE // 2] if "left" in direction else tile1[0, TILE_SIZE // 2:]
        edge2 = tile2[-1, :TILE_SIZE // 2] if "left" in direction else tile2[-1, TILE_SIZE // 2:]
    elif direction in ["down_left", "down_right"]:
        edge1 = tile1[-1, :TILE_SIZE // 2] if "left" in direction else tile1[-1, TILE_SIZE // 2:]
        edge2 = tile2[0, :TILE_SIZE // 2] if "left" in direction else tile2[0, TILE_SIZE // 2:]
    else:
        return 0

    if is_edge_section_transparent(edge1) or is_edge_section_transparent(edge2):
        return 0

    edge1_gray = cv2.cvtColor(np.expand_dims(edge1, axis=0), cv2.COLOR_BGR2GRAY)
    edge2_gray = cv2.cvtColor(np.expand_dims(edge2, axis=0), cv2.COLOR_BGR2GRAY)

    win_size = min(7, min(edge1_gray.shape[0], edge1_gray.shape[1]))
    if win_size % 2 == 0: win_size -= 1
    if win_size < 3:
        return mse(edge1_gray, edge2_gray)

    return ssim(edge1_gray, edge2_gray, win_size=win_size, channel_axis=None)

# === Main Processing Loop ===
tileset_images = [f for f in os.listdir(TILESET_FOLDER) if f.endswith(".png")]

for tileset in tileset_images:
    tileset_id = os.path.splitext(tileset)[0]
    tileset_folder = os.path.join(SPLIT_TILE_FOLDER, tileset_id)

    if not os.path.exists(tileset_folder):
        print(f"[SKIP] Folder not found: {tileset_folder}")
        continue

    tile_files = [f for f in os.listdir(tileset_folder) if f.startswith("tiles_") and f.endswith(".png")]
    tile_coords = [(int(f.split("_")[1]), int(f.split("_")[2].split(".")[0])) for f in tile_files]
    if not tile_coords:
        print(f"[SKIP] No tiles found in {tileset_folder}")
        continue

    max_x = max(coord[0] for coord in tile_coords) + 1
    max_y = max(coord[1] for coord in tile_coords) + 1

    results = []

    for x, y in tile_coords:
        tile = load_tile(tileset_id, x, y)
        if tile is None:
            continue

        edge_transparency = check_edge_transparency(tile)
        connectivity_list = []
        possible_connectivity_list = []

        directions = {
            "right_top": (x + 1, y),
            "right_down": (x + 1, y),
            "left_top": (x - 1, y),
            "left_down": (x - 1, y),
            "top_left": (x, y - 1),
            "top_right": (x, y - 1),
            "down_left": (x, y + 1),
            "down_right": (x, y + 1),
        }

        for direction, (nx, ny) in directions.items():
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                continue

            # if edge_transparency.get(direction) is False:
            # if edge_transparency.get(direction) is False or direction in ["top_left", "right_down", "left_down"]:
            if direction in edge_transparency and not edge_transparency[direction]:

                possible_connectivity_list.append(direction)
                neighbor_tile = load_tile(tileset_id, nx, ny)
                if neighbor_tile is not None:
                    score = compare_edges(tile, neighbor_tile, direction)
                    if score > SSIM_THRESHOLD:
                        connectivity_list.append(direction)

        results.append({
            "tile_x": x,
            "tile_y": y,
            "connectivity": connectivity_list,
            "possible_connectivity": possible_connectivity_list,
            "edge_transparency": edge_transparency
        })

    output_file = os.path.join(OUTPUT_FOLDER, f"tile_connectivity-{tileset_id}.json")
    print(f"[SAVE] {tileset_id}: {len(results)} tiles → {output_file}")
    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4, default=lambda x: bool(x) if isinstance(x, np.bool_) else x)

print("✅ All smart connectivity results saved.")
