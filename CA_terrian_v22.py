import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from collections import defaultdict, Counter
import json

# -------------------- Parameters --------------------
MAP_WIDTH, MAP_HEIGHT = 30, 20
# TILE_EMPTY, TILE_BASE = 0, 1
TILE_EMPTY = 0
TILE_BASE = 1
TILE_PATCH = 2
TILE_INTERACTIVE = 3
TILE_ITEM = 4

BASE_PROB, PATCH_PROB = 0.45, 0.4
BASE_ITER, PATCH_ITER = 4, 3
PATCH_MIN_SIZE = 20
USE_FIXED_SEED = True
BASE_SEED, PATCH_SEED = 42, 1234
JSON_PATH = "StoryFiles/2_object_affordance_langchain.json"  # or use "2_..." for Story 2

material_like = {
    "grass", "rock", "mud", "wood", "stone", "dirt", "concrete", "indoor", "outdoor",
    "sand", "soil", "metal", "urban", "office"
}

# -------------------- Utility Functions --------------------
def initialize_map(prob, tile_val, seed):
    np.random.seed(seed)
    return np.where(np.random.rand(MAP_HEIGHT, MAP_WIDTH) < prob, tile_val, TILE_EMPTY)

def smooth_map(grid, tile_val, iterations):
    for _ in range(iterations):
        new = grid.copy()
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                neighbors = grid[max(0,y-1):min(MAP_HEIGHT,y+2), max(0,x-1):min(MAP_WIDTH,x+2)]
                count = np.count_nonzero(neighbors == tile_val)
                new[y,x] = tile_val if count >= 5 else TILE_EMPTY
        grid = new
    return grid

def connect_largest_region(grid, tile_val):
    labeled, num = label(grid == tile_val)
    if num == 0: return np.zeros_like(grid)
    largest = np.argmax(np.bincount(labeled.flat)[1:]) + 1
    return (labeled == largest).astype(int) * tile_val

def print_matrix(name, mat):
    print(f"\n{name}:\n" + "\n".join("".join(str(c) for c in row) for row in mat))

# -------------------- Load JSON --------------------
with open(JSON_PATH, "r", encoding="utf-8") as f:
    story_data = json.load(f)

scenes = story_data["per_scene_affordances"]

# -------------------- Pass 1: Collect Bases and Patches --------------------
base_names = set()
patch_names = set()
scene_base_choice = {}
scene_terrain_objs = {}

for scene in scenes:
    title = scene["scene_title"]
    terrs = [obj["suggested_terrain"].lower() for obj in scene["objects"] if obj["suggested_terrain"].lower() not in {"any", "n/a"}]
    freqs = Counter(terrs)
    chosen = next((t for t, _ in freqs.most_common() if t in material_like), None) or (freqs.most_common(1)[0][0] if freqs else "grass")
    scene_base_choice[title] = chosen
    base_names.add(chosen)

    terrain_objs = [obj["object"].lower().replace(" ", "_") for obj in scene["objects"] if obj.get("affordance_category") == "Terrain"]
    scene_terrain_objs[title] = terrain_objs
    patch_names.update(terrain_objs)

# -------------------- Generate Base Areas --------------------
base_areas = {}
for i, name in enumerate(sorted(base_names)):
    seed = BASE_SEED + i if USE_FIXED_SEED else np.random.randint(0,9999)
    base = initialize_map(BASE_PROB, TILE_BASE, seed)
    base = smooth_map(base, TILE_BASE, BASE_ITER)
    base = connect_largest_region(base, TILE_BASE)
    base_areas[name] = base
    print_matrix(f"Base: {name}", base)

# -------------------- Generate Patch Maps --------------------
patch_areas = {}
used_mask = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=bool)
for i, name in enumerate(sorted(patch_names)):
    seed = PATCH_SEED + i if USE_FIXED_SEED else np.random.randint(0,9999)
    raw = initialize_map(PATCH_PROB, i+2, seed)
    raw = smooth_map(raw, i+2, PATCH_ITER)
    patch = connect_largest_region(raw, i+2)
    patch = np.where(used_mask | (patch == 0), TILE_EMPTY, patch)
    if np.sum(patch > 0) >= PATCH_MIN_SIZE:
        patch_areas[name] = patch
        used_mask |= (patch > 0)
        print_matrix(f"Patch: {name}", patch)

# -------------------- Scene Assembly and Visualization --------------------
fig1, axs1 = plt.subplots(len(scenes), 3, figsize=(12, 4 * len(scenes)))  # Step 1
fig2, axs2 = plt.subplots(len(scenes), 2, figsize=(10, 4 * len(scenes)))  # Step 2

for idx, scene in enumerate(scenes):
    title = scene["scene_title"]
    base_name = scene_base_choice[title]
    base = base_areas[base_name]
    terrain_objs = scene_terrain_objs[title]

    # Step 1a: show text title
    axs1[idx, 0].text(0.1, 0.5, title, fontsize=12)
    axs1[idx, 0].axis("off")

    # Step 1b: base visualization
    axs1[idx, 1].imshow(base, cmap="Greens", vmin=0, vmax=2)
    axs1[idx, 1].set_title(f"Base: {base_name}")
    axs1[idx, 1].axis("off")

    # Step 1c: patch visualization
    patch_layer = np.zeros_like(base)
    patch_labels = []
    for p in patch_names:
        if p in patch_areas and p in terrain_objs:
            patch_layer = np.where(patch_areas[p] > 0, TILE_BASE + 1, patch_layer)
            patch_labels.append(p)

    axs1[idx, 2].imshow(patch_layer, cmap="Oranges", vmin=0, vmax=2)
    axs1[idx, 2].set_title("Patches: " + ", ".join(patch_labels) if patch_labels else "No patch")
    axs1[idx, 2].axis("off")

    # Step 2a: text summary
    obj_list = [obj["object"].lower() for obj in scene["objects"]]
    info = f"Base: {base_name}\nObjects: " + ", ".join(obj_list)
    axs2[idx, 0].text(0.01, 0.5, info, fontsize=10)
    axs2[idx, 0].axis("off")

    # Step 2b: combined map (union base + patch)
    combined = np.where(patch_layer > 0, TILE_PATCH, base)
    axs2[idx, 1].imshow(combined, cmap="tab20", vmin=0, vmax=5)
    axs2[idx, 1].set_title(f"Scene {idx+1} Combined")
    axs2[idx, 1].axis("off")

    print_matrix(f"Scene Union [{title}]", combined)

plt.tight_layout()
plt.show()
