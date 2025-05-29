import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from collections import defaultdict
import json
from pathlib import Path

SAVE_OUT_FOLDER = "StoryFiles/"
FILE_NUMBER = 1 #"StoryFiles/"+FILE_NUMBER+"

# ---------------- Config ----------------
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY, TILE_BASE, TILE_PATCH = 0, 1, 2
BASE_PROB, PATCH_PROB = 0.65, 0.5
BASE_ITER, PATCH_ITER = 4, 3
PATCH_MIN_SIZE = 20
USE_FIXED_SEED = False
BASE_SEED, PATCH_SEED = 42, 1234

# ---------------- File Paths ----------------
AFFORDANCE_PATH =SAVE_OUT_FOLDER + str(FILE_NUMBER)+"_object_affordance_langchain.json"
DECISION_PATH = SAVE_OUT_FOLDER + str(FILE_NUMBER)+"_scene_generation_decisions.json"
MATRIX_LOG_PATH = SAVE_OUT_FOLDER + str(FILE_NUMBER)+"_tile_matrix_output.json"

# ---------------- Utilities ----------------
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
    from scipy.ndimage import label
    labeled, num = label(grid == tile_val)
    if num == 0: return np.zeros_like(grid)
    largest = np.argmax(np.bincount(labeled.flat)[1:]) + 1
    return (labeled == largest).astype(int) * tile_val

def to_matrix_list(grid):
    return [[int(cell) for cell in row] for row in grid]

# ---------------- Load Files ----------------
with open(AFFORDANCE_PATH, "r", encoding="utf-8") as f:
    affordance_data = json.load(f)

with open(DECISION_PATH, "r", encoding="utf-8") as f:
    decision_data = json.load(f)

scene_titles = [s["scene_title"] for s in decision_data]

# ---------------- Generate Base Maps ----------------
unique_bases = sorted(set(s["chosen_base"] for s in decision_data))
base_maps = {}
matrix_log = {"base_maps": {}, "patch_maps": {}, "scene_maps": {}}

for i, base in enumerate(unique_bases):
    seed = BASE_SEED + i if USE_FIXED_SEED else np.random.randint(0, 9999)
    mat = initialize_map(BASE_PROB, TILE_BASE, seed)
    mat = smooth_map(mat, TILE_BASE, BASE_ITER)
    mat = connect_largest_region(mat, TILE_BASE)
    base_maps[base] = mat
    matrix_log["base_maps"][base] = to_matrix_list(mat)

# ---------------- Generate Patch Maps ----------------
patch_names = sorted({p for s in decision_data for p in s["final_patch_for_base"] if p != "<no patch>"})
patch_maps = {}
used_mask = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=bool)

for i, patch in enumerate(patch_names):
    seed = PATCH_SEED + i if USE_FIXED_SEED else np.random.randint(0, 9999)
    raw = initialize_map(PATCH_PROB, TILE_PATCH, seed)
    raw = smooth_map(raw, TILE_PATCH, PATCH_ITER)
    patch_mat = connect_largest_region(raw, TILE_PATCH)
    patch_mat = np.where(used_mask | (patch_mat == 0), TILE_EMPTY, patch_mat)
    if np.sum(patch_mat > 0) >= PATCH_MIN_SIZE:
        patch_maps[patch] = patch_mat
        used_mask |= (patch_mat > 0)
        matrix_log["patch_maps"][patch] = to_matrix_list(patch_mat)

# ---------------- Step 1: Scene Visualization ----------------
fig1, axs1 = plt.subplots(len(decision_data), 3, figsize=(12, 4 * len(decision_data)))

for idx, scene in enumerate(decision_data):
    title = scene["scene_title"]
    base = base_maps[scene["chosen_base"]]
    patch_layer = np.zeros_like(base)

    for p in scene["final_patch_for_base"]:
        if p in patch_maps:
            patch_layer = np.where(patch_maps[p] > 0, TILE_PATCH, patch_layer)

    # 3 Columns: Title | Base | Patch(s)
    axs1[idx, 0].text(0.1, 0.5, title, fontsize=12)
    axs1[idx, 0].axis("off")

    axs1[idx, 1].imshow(base, cmap="Greens", vmin=0, vmax=2)
    axs1[idx, 1].set_title(f"Base: {scene['chosen_base']}")
    axs1[idx, 1].axis("off")

    axs1[idx, 2].imshow(patch_layer, cmap="Oranges", vmin=0, vmax=2)
    axs1[idx, 2].set_title("Patch: " + ", ".join(scene["final_patch_for_base"]))
    axs1[idx, 2].axis("off")

plt.tight_layout()
plt.show()

# ---------------- Step 2: Combined Scene Maps ----------------
fig2, axs2 = plt.subplots(len(decision_data), 2, figsize=(10, 4 * len(decision_data)))

for idx, scene in enumerate(decision_data):
    title = scene["scene_title"]
    base = base_maps[scene["chosen_base"]]
    patch_layer = np.zeros_like(base)

    for p in scene["final_patch_for_base"]:
        if p in patch_maps:
            patch_layer = np.where(patch_maps[p] > 0, TILE_PATCH, patch_layer)

    combined = np.where(patch_layer > 0, TILE_PATCH, base)

    # Save to matrix log
    matrix_log["scene_maps"][title] = {
        "base": to_matrix_list(base),
        "patch": to_matrix_list(patch_layer),
        "combined": to_matrix_list(combined)
    }

    # Col 1: text summary
    info = f"Base: {scene['chosen_base']}\nPatch(es): " + ", ".join(scene["final_patch_for_base"])
    axs2[idx, 0].text(0.01, 0.5, info, fontsize=10)
    axs2[idx, 0].axis("off")

    # Col 2: combined map
    axs2[idx, 1].imshow(combined, cmap="tab20", vmin=0, vmax=5)
    axs2[idx, 1].set_title(f"Scene {idx+1}: {title}")
    axs2[idx, 1].axis("off")

plt.tight_layout()
plt.show()

# ---------------- Write matrix output to file ----------------
with open(MATRIX_LOG_PATH, "w", encoding="utf-8") as f:
    json.dump(matrix_log, f, indent=2)

print(f"\n✅ Tile matrix log saved to: {MATRIX_LOG_PATH}")
