import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
import json
import random
from collections import Counter

# =================== Configurations ====================
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY, TILE_BASE, TILE_PATCH = 0, 1, 2
BASE_PROB, BASE_ITER = 0.60, 4
PATCH_PROB, PATCH_ITER = 0.45, 3
PATCH_MIN_SIZE = 20
USE_FIXED_SEED = True
BASE_SEED = 42
PATCH_SEED = 999
MAX_SCENES = 3
INPUT_JSON = "StoryFiles/1_object_affordance_langchain.json"

# ============== Helper Functions =======================
def initialize_map(prob, tile_val, seed):
    np.random.seed(seed)
    return np.where(np.random.rand(MAP_HEIGHT, MAP_WIDTH) < prob, tile_val, TILE_EMPTY)

def smooth_map(grid, tile_val, iterations):
    for _ in range(iterations):
        new_grid = grid.copy()
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                neighbors = grid[max(0, y-1):min(MAP_HEIGHT, y+2), max(0, x-1):min(MAP_WIDTH, x+2)]
                count = np.count_nonzero(neighbors == tile_val)
                new_grid[y, x] = tile_val if count >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

def connect_largest_region(grid, tile_val):
    labeled, num = label(grid == tile_val)
    if num == 0:
        return np.zeros_like(grid)
    largest = np.argmax(np.bincount(labeled.flat)[1:]) + 1
    return (labeled == largest).astype(int) * tile_val

def extract_terrain_info(scene_objects):
    terrain_suggestions = []
    terrain_objects = []
    for obj in scene_objects:
        terrain = obj["suggested_terrain"].lower().strip()
        if obj["category"].lower() == "terrain":
            terrain_objects.append(obj)
        if terrain not in ["any", "n/a"]:
            terrain_suggestions += [t.strip() for t in terrain.split(",")]
    base = Counter(terrain_suggestions).most_common(1)[0][0] if terrain_suggestions else "grass"
    patch_terrains = list({x["object"].lower().replace(" ", "_") for x in terrain_objects})
    return base, patch_terrains

def print_log(idx, scene_title, base_name, patch_name):
    print(f"Scene {idx+1}: {scene_title}")
    print(f"  Base terrain: {base_name}")
    print(f"  Patch terrain: {patch_name if patch_name else '[None, use base area]'}")

# =============== Load Input JSON =======================
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# =============== Scene Map Generation ==================
fig, axs = plt.subplots(MAX_SCENES, 3, figsize=(15, 5 * MAX_SCENES))
prev_base_name, prev_patch_name = None, None
prev_base, prev_patch = None, None

for idx in range(min(MAX_SCENES, len(data["per_scene_affordances"]))):
    scene = data["per_scene_affordances"][idx]
    scene_objects = scene["objects"]
    scene_title = scene["scene_title"]

    base_name, patch_terrains = extract_terrain_info(scene_objects)
    patch_name = patch_terrains[0] if patch_terrains else None

    # Determine base map
    if idx == 0 or base_name != prev_base_name:
        base_seed = BASE_SEED + idx if USE_FIXED_SEED else random.randint(0, 9999)
        base = initialize_map(BASE_PROB, TILE_BASE, base_seed)
        base = smooth_map(base, TILE_BASE, BASE_ITER)
        base = connect_largest_region(base, TILE_BASE)
    else:
        base = prev_base.copy()

    # Determine patch
    if idx == 0 or patch_name != prev_patch_name or base_name != prev_base_name:
        patch = np.zeros_like(base)
        if patch_name:
            patch_seed = PATCH_SEED + idx if USE_FIXED_SEED else random.randint(0, 9999)
            raw_patch = initialize_map(PATCH_PROB, TILE_PATCH, patch_seed)
            raw_patch = smooth_map(raw_patch, TILE_PATCH, PATCH_ITER)
            patch = connect_largest_region(raw_patch, TILE_PATCH)
            if np.sum(patch == TILE_PATCH) < PATCH_MIN_SIZE:
                patch = np.zeros_like(base)
        else:
            patch = np.where(base == TILE_BASE, TILE_PATCH, TILE_EMPTY)
            patch_name = base_name + "_area"
    else:
        patch = prev_patch.copy()

    combined = np.where(patch > 0, patch, base)

    print_log(idx, scene_title, base_name, patch_name)

    # Plotting
    cmap = plt.get_cmap("tab20", 3)
    axs[idx, 0].imshow(base, cmap=cmap, vmin=0, vmax=2)
    axs[idx, 0].set_title(f"{scene_title}\nBase: {base_name}")
    axs[idx, 0].axis("off")

    axs[idx, 1].imshow(patch, cmap=cmap, vmin=0, vmax=2)
    axs[idx, 1].set_title(f"Patch: {patch_name}")
    axs[idx, 1].axis("off")

    axs[idx, 2].imshow(combined, cmap=cmap, vmin=0, vmax=2)
    axs[idx, 2].set_title("Combined")
    axs[idx, 2].axis("off")

    # Store for reuse
    prev_base_name, prev_patch_name = base_name, patch_name
    prev_base, prev_patch = base, patch

plt.tight_layout()
plt.show()
