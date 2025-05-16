import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import deque
import random
import time

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY = 0
TILE_BASE = 1
TILE_PATCH_START = 2

USE_FIXED_SEED = True
SEED_BASE = 42

BASE_PROB = 0.65
BASE_ITER = 4

PATCH_PROB = 0.50
PATCH_ITER = 2
MIN_PATCH_TILES = 30
MAX_ATTEMPTS = 50

# --- PATCH CONFIGS (data-driven) ---
patch_configs = [
    {"name": "Patch_A", "seed": 100},
    {"name": "Patch_B", "seed": 200},
    {"name": "Patch_C", "seed": 300},
]

# --- SEED HANDLING ---
if USE_FIXED_SEED:
    base_seed = SEED_BASE
else:
    base_seed = int(time.time()) % 100000

# --- FUNCTIONS ---
def initialize_map(prob, tile_type, seed):
    np.random.seed(seed)
    return np.random.choice([TILE_EMPTY, tile_type], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

def smooth_map(grid, tile_type, iterations):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                neighbors = sum(
                    0 <= x+dx < grid.shape[0] and 0 <= y+dy < grid.shape[1] and grid[x+dx, y+dy] == tile_type
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = tile_type if neighbors >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

def connect_largest_region(grid, tile_type):
    visited = np.zeros_like(grid, dtype=bool)
    def flood_fill(x, y):
        region = []
        queue = deque([(x, y)])
        visited[x, y] = True
        while queue:
            cx, cy = queue.popleft()
            region.append((cx, cy))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                    if not visited[nx, ny] and grid[nx, ny] == tile_type:
                        visited[nx, ny] = True
                        queue.append((nx, ny))
        return region

    regions = []
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == tile_type and not visited[x, y]:
                regions.append(flood_fill(x, y))

    if not regions:
        return np.full_like(grid, TILE_EMPTY)

    largest = max(regions, key=len)
    new_grid = np.full_like(grid, TILE_EMPTY)
    for x, y in largest:
        new_grid[x, y] = tile_type
    return new_grid

# --- GENERATE BASE TERRAIN ---
base = initialize_map(BASE_PROB, TILE_BASE, base_seed)
base = smooth_map(base, TILE_BASE, BASE_ITER)
base = connect_largest_region(base, TILE_BASE)

# --- INITIALIZE COMBINED MAP AND COLOR MAP ---
combined = base.copy()
color_map = {TILE_EMPTY: (1, 1, 1), TILE_BASE: (random.random(), random.random(), random.random())}
legend_labels = [("0: Empty", TILE_EMPTY), ("1: Base", TILE_BASE)]

# --- EXPANDABLE BASE THAT INCLUDES PATCHES ---
expanded_base = base.copy()

# --- GENERATE AND OVERLAY PATCHES ---
for i, cfg in enumerate(patch_configs):
    patch_id = TILE_PATCH_START + i
    attempt = 0
    patch = np.full((MAP_HEIGHT, MAP_WIDTH), TILE_EMPTY)

    while attempt < MAX_ATTEMPTS:
        seed = cfg["seed"] + attempt
        temp = initialize_map(PATCH_PROB, patch_id, seed)
        temp = smooth_map(temp, patch_id, PATCH_ITER)
        temp = connect_largest_region(temp, patch_id)

        patch_mask = (temp == patch_id)
        if np.sum(patch_mask) >= MIN_PATCH_TILES:
            patch = temp
            print(f"✅ {cfg['name']} placed with ID {patch_id} using seed {seed}, tiles: {np.sum(patch_mask)}")
            break
        attempt += 1
    else:
        print(f"❌ {cfg['name']} failed after {MAX_ATTEMPTS} attempts.")

    # Overlay patch on combined map (allow overlaps)
    combined = np.where(patch == patch_id, patch_id, combined)

    # Expand base to include patch region
    expanded_base = np.where(patch == patch_id, TILE_BASE, expanded_base)

    # Register color
    color_map[patch_id] = (random.random(), random.random(), random.random())
    legend_labels.append((f"{patch_id}: {cfg['name']}", patch_id))

# --- VISUALIZATION ---
cmap_list = [color_map[i] for i in sorted(color_map)]
cmap = plt.matplotlib.colors.ListedColormap(cmap_list)

plt.figure(figsize=(10, 6))
plt.imshow(combined, cmap=cmap, origin='upper')
plt.title("Combined Map (Base + All Patches)")
plt.axis("off")

legend_elements = [
    Patch(facecolor=color_map[tile], edgecolor='black', label=label)
    for label, tile in legend_labels
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# --- OUTPUT MATRICES ---
print("\nExpanded Base (Base + Patch Tiles):")
print(expanded_base)

print("\nFinal Combined Map (Visualized):")
print(combined)
