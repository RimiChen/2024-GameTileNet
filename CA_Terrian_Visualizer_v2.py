import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from collections import defaultdict, Counter
import json



SAVE_OUT_FOLDER = "StoryFiles/"
FILE_NUMBER = 2 #"StoryFiles/"+FILE_NUMBER+"

# -------------------- Config --------------------
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY, TILE_BASE, TILE_PATCH = 0, 1, 2
BASE_PROB, PATCH_PROB = 0.65, 0.5
BASE_ITER, PATCH_ITER = 4, 3
PATCH_MIN_SIZE = 20
USE_FIXED_SEED = True
BASE_SEED, PATCH_SEED = 42, 1234
JSON_PATH = SAVE_OUT_FOLDER + str(FILE_NUMBER)+"_object_affordance_langchain.json"  # or switch to story 2 if needed

MATERIAL_LIKE = {
    "grass", "rock", "mud", "wood", "stone", "dirt", "concrete", "indoor", "outdoor",
    "sand", "soil", "metal", "urban", "office"
}
TERRAIN_KEYWORDS = ["room", "alley", "hall", "corridor", "path", "cave", "lab", "arena"]

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
    data = json.load(f)

scenes = data["per_scene_affordances"]

# -------------------- Step 1: Base + Patch Detection --------------------
scene_info = []
base_to_patches = defaultdict(set)

for scene in scenes:
    title = scene["scene_title"]
    suggested = [
        t.strip() for obj in scene["objects"]
        for t in obj["suggested_terrain"].lower().split(",")
        if obj["suggested_terrain"].lower() not in {"any", "n/a"}
    ]
    freqs = Counter(suggested)
    base = next((t for t, _ in freqs.most_common() if t in MATERIAL_LIKE), None)
    base = base or freqs.most_common(1)[0][0] if freqs else "grass"

    detected_patches = [
        obj["object"].lower().replace(" ", "_")
        for obj in scene["objects"]
        if any(k in obj["object"].lower() for k in TERRAIN_KEYWORDS)
    ]
    for p in detected_patches:
        base_to_patches[base].add(p)

    scene_info.append({
        "scene_title": title,
        "base": base,
        "objects": [obj["object"].lower().replace(" ", "_") for obj in scene["objects"]],
        "patches_for_scene": detected_patches
    })

# Propagate patches for shared base
for s in scene_info:
    s["patches_combined"] = sorted(base_to_patches[s["base"]]) if base_to_patches[s["base"]] else ["<no patch>"]

# -------------------- Step 2: Generate Base Maps --------------------
base_maps = {}
for i, base in enumerate(sorted(set(s["base"] for s in scene_info))):
    seed = BASE_SEED + i if USE_FIXED_SEED else np.random.randint(0, 9999)
    mat = initialize_map(BASE_PROB, TILE_BASE, seed)
    mat = smooth_map(mat, TILE_BASE, BASE_ITER)
    mat = connect_largest_region(mat, TILE_BASE)
    base_maps[base] = mat
    print_matrix(f"Base [{base}]", mat)

# -------------------- Step 3: Generate Patch Maps --------------------
patch_maps = {}
used_mask = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=bool)
for i, name in enumerate(sorted(set(p for s in scene_info for p in s["patches_combined"] if p != "<no patch>"))):
    seed = PATCH_SEED + i if USE_FIXED_SEED else np.random.randint(0, 9999)
    raw = initialize_map(PATCH_PROB, TILE_PATCH, seed)
    raw = smooth_map(raw, TILE_PATCH, PATCH_ITER)
    patch = connect_largest_region(raw, TILE_PATCH)
    patch = np.where(used_mask | (patch == 0), TILE_EMPTY, patch)
    if np.sum(patch > 0) >= PATCH_MIN_SIZE:
        used_mask |= (patch > 0)
        patch_maps[name] = patch
        print_matrix(f"Patch [{name}]", patch)

# -------------------- Step 4: Visualization Step 1 --------------------
fig1, axs1 = plt.subplots(len(scene_info), 3, figsize=(12, 4 * len(scene_info)))

for idx, scene in enumerate(scene_info):
    title = scene["scene_title"]
    base_name = scene["base"]
    base = base_maps[base_name]
    patch_layer = np.zeros_like(base)
    for patch in scene["patches_combined"]:
        if patch in patch_maps:
            patch_layer = np.where(patch_maps[patch] > 0, TILE_PATCH, patch_layer)

    # Col 1: Scene Title
    axs1[idx, 0].text(0.1, 0.5, title, fontsize=12)
    axs1[idx, 0].axis("off")

    # Col 2: Base
    axs1[idx, 1].imshow(base, cmap="Greens", vmin=0, vmax=2)
    axs1[idx, 1].set_title(f"Base: {base_name}")
    axs1[idx, 1].axis("off")

    # Col 3: Patch
    axs1[idx, 2].imshow(patch_layer, cmap="Oranges", vmin=0, vmax=2)
    axs1[idx, 2].set_title("Patches: " + ", ".join(scene["patches_combined"]))
    axs1[idx, 2].axis("off")

plt.tight_layout()
plt.show()

# -------------------- Step 5: Visualization Step 2 --------------------
fig2, axs2 = plt.subplots(len(scene_info), 2, figsize=(10, 4 * len(scene_info)))

for idx, scene in enumerate(scene_info):
    base = base_maps[scene["base"]]
    patch_layer = np.zeros_like(base)
    for patch in scene["patches_combined"]:
        if patch in patch_maps:
            patch_layer = np.where(patch_maps[patch] > 0, TILE_PATCH, patch_layer)
    combined = np.where(patch_layer > 0, TILE_PATCH, base)

    # Col 1: text summary
    summary = f"Base: {scene['base']}\nObjects: " + ", ".join(scene["objects"])
    axs2[idx, 0].text(0.01, 0.5, summary, fontsize=10)
    axs2[idx, 0].axis("off")

    # Col 2: Combined map
    axs2[idx, 1].imshow(combined, cmap="tab20", vmin=0, vmax=5)
    axs2[idx, 1].set_title(f"Scene {idx+1} Combined")
    axs2[idx, 1].axis("off")

    print_matrix(f"Scene Combined [{scene['scene_title']}]", combined)

plt.tight_layout()
plt.show()
