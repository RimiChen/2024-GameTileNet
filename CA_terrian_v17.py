import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.ndimage import label

# --- Parameters ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY, TILE_BASE = 0, 1
BASE_PROB, BASE_ITER = 0.45, 4
PATCH_PROB, PATCH_ITER = 0.40, 3
NUM_PATCHES = 2
MIN_PATCH_SIZE = 30
USE_FIXED_SEED = False
BASE_SEED = 42
PATCH_SEED_BASE = 1000

# --- Functions ---
def initialize_map(prob, tile_val, seed):
    np.random.seed(seed)
    return np.where(np.random.rand(MAP_HEIGHT, MAP_WIDTH) < prob, tile_val, TILE_EMPTY)

def smooth_map(grid, tile_val, iterations=4):
    for _ in range(iterations):
        new_grid = grid.copy()
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                neighbors = grid[max(0,y-1):min(MAP_HEIGHT,y+2), max(0,x-1):min(MAP_WIDTH,x+2)]
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

def visualize(grid, title, cmap=None):
    plt.figure(figsize=(10, 6))
    plt.imshow(grid, cmap=cmap if cmap else "tab20", vmin=0, vmax=NUM_PATCHES+1)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

# --- Generate Base ---
base_seed = BASE_SEED if USE_FIXED_SEED else random.randint(0, 9999)
base = initialize_map(BASE_PROB, TILE_BASE, base_seed)
base = smooth_map(base, TILE_BASE, BASE_ITER)
base = connect_largest_region(base, TILE_BASE)
print("📦 Base Map (1 = terrain):")
print(base)
visualize(base, "Base Map")

# --- Generate Patches (stored separately) ---
patch_maps = []
for i in range(NUM_PATCHES):
    patch_val = i + 2  # patch tile value (2, 3, ...)
    patch_seed = PATCH_SEED_BASE + i if USE_FIXED_SEED else random.randint(0, 9999)
    patch = initialize_map(PATCH_PROB, patch_val, patch_seed)
    patch = smooth_map(patch, patch_val, PATCH_ITER)
    patch = connect_largest_region(patch, patch_val)
    if np.sum(patch == patch_val) >= MIN_PATCH_SIZE:
        patch_maps.append(patch)
        print(f"✅ Patch {i} with value {patch_val} has {np.sum(patch == patch_val)} tiles")
        visualize(patch, f"Patch {i+1} Map (value={patch_val})")
    else:
        print(f"⚠️ Patch {i} too small and skipped.")

# --- Expand Base (Union of base and patches) ---
expanded_base = base.copy()
for patch_map in patch_maps:
    expanded_base = np.where(patch_map > 0, TILE_BASE, expanded_base)

# --- Ensure Expanded Base is Connected ---
expanded_base_connected = connect_largest_region(expanded_base, TILE_BASE)
print("\n🌿 Final Connected Expanded Base (1 = walkable):")
print(expanded_base_connected)
visualize(expanded_base_connected, "Final Connected Expanded Base")
