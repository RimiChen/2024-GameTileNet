import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
import random
import json
from collections import Counter

# ----------------------------- PARAMETERS -----------------------------
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY, TILE_BASE = 0, 1
BASE_PROB, BASE_ITER = 0.75, 4
PATCH_PROB, PATCH_ITER = 0.60, 3
PATCH_MIN_SIZE = 20
USE_FIXED_SEED = True
BASE_SEED = 42
PATCH_SEED = 99

json_path = "StoryFiles/2_object_affordance_langchain.json"

# ----------------------------- UTILITIES -----------------------------
def initialize_map(prob, tile_val, seed):
    np.random.seed(seed)
    return np.where(np.random.rand(MAP_HEIGHT, MAP_WIDTH) < prob, tile_val, TILE_EMPTY)

def smooth_map(grid, tile_val, iterations):
    for _ in range(iterations):
        new_grid = grid.copy()
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                neighbors = grid[max(0, y-1):min(MAP_HEIGHT, y+2), max(0, x-1):min(MAP_WIDTH,x+2)]
                count = np.count_nonzero(neighbors == tile_val)
                new_grid[y, x] = tile_val if count >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

def connect_largest_region(grid, tile_val):
    mask = (grid == tile_val)
    labeled, num = label(mask)
    if num == 0:
        return np.full_like(grid, TILE_EMPTY)
    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0
    largest = sizes.argmax()
    return np.where(labeled == largest, tile_val, TILE_EMPTY)

def visualize(grid, title, tile_label_map):
    cmap = plt.get_cmap("tab20", max(tile_label_map.keys()) + 1)
    plt.figure(figsize=(8, 5))
    plt.imshow(grid, cmap=cmap, vmin=0, vmax=max(tile_label_map.keys()))
    cbar = plt.colorbar(ticks=list(tile_label_map.keys()))
    cbar.ax.set_yticklabels(tile_label_map.values())
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

# ----------------------------- LOAD SCENE -----------------------------
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

scene = data["per_scene_affordances"][0]
scene_title = scene["scene_title"]
scene_objects = scene["objects"]

terrain_suggestions = []
terrain_objects = []

for obj in scene_objects:
    terrain = obj["suggested_terrain"].lower().strip()
    if obj["category"].lower() == "terrain":
        terrain_objects.append(obj)
    if terrain not in ["any", "n/a"]:
        terrain_suggestions.extend([x.strip() for x in terrain.split(",")])

fallback_terrain = Counter(terrain_suggestions).most_common(1)[0][0] if terrain_suggestions else "grass"
base_terrain = fallback_terrain
patch_terrains = list({x["object"].lower().replace(" ", "_") for x in terrain_objects}) if terrain_objects else []

# ----------------------------- GENERATE BASE -----------------------------
base_seed = BASE_SEED if USE_FIXED_SEED else random.randint(0, 9999)
base = initialize_map(BASE_PROB, TILE_BASE, base_seed)
base = smooth_map(base, TILE_BASE, BASE_ITER)
base = connect_largest_region(base, TILE_BASE)

# ----------------------------- GENERATE PATCH OR DEFAULT -----------------------------
patch = np.zeros_like(base)
tile_label_map = {0: "empty", 1: base_terrain}
patch_val = 2

if patch_terrains:
    patch_seed = PATCH_SEED if USE_FIXED_SEED else random.randint(0, 9999)
    patch_raw = initialize_map(PATCH_PROB, patch_val, patch_seed)
    patch_raw = smooth_map(patch_raw, patch_val, PATCH_ITER)
    patch = connect_largest_region(patch_raw, patch_val)
    if np.sum(patch == patch_val) < PATCH_MIN_SIZE:
        patch = np.zeros_like(base)
    else:
        tile_label_map[patch_val] = patch_terrains[0]
else:
    patch = np.where(base == TILE_BASE, patch_val, TILE_EMPTY)
    tile_label_map[patch_val] = base_terrain + "_area"

# ----------------------------- VISUALIZATION -----------------------------
combined = np.where(patch > 0, patch, base)

print(f"Scene: {scene_title}")
print(f"Base terrain: {base_terrain}")
print(f"Patch terrain(s): {patch_terrains if patch_terrains else ['(default area from base)']}")

visualize(base, "Base Map", tile_label_map)
visualize(patch, "Patch Map (Level 0)", tile_label_map)
visualize(combined, "Combined Map (Base + Patch)", tile_label_map)
