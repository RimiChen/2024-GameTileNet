import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import deque

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY = 0
TILE_BASE = 1
TILE_PATCH = 2

SEED_BASE = 42
SEED_PATCH = 123

BASE_PROB = 0.65
PATCH_PROB = 0.50

BASE_ITER = 4
PATCH_ITER = 2

MIN_PATCH_TILES = 30
MAX_ATTEMPTS = 50

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

# --- GENERATE BASE (Level -1) ---
base = initialize_map(BASE_PROB, TILE_BASE, SEED_BASE)
base = smooth_map(base, TILE_BASE, BASE_ITER)
base = connect_largest_region(base, TILE_BASE)

# --- GENERATE PATCH (Level 0) with retry if too small ---
attempt = 0
patch = np.full((MAP_HEIGHT, MAP_WIDTH), TILE_EMPTY)

while attempt < MAX_ATTEMPTS:
    temp = initialize_map(PATCH_PROB, TILE_PATCH, SEED_PATCH + attempt)
    temp = smooth_map(temp, TILE_PATCH, PATCH_ITER)
    temp = connect_largest_region(temp, TILE_PATCH)
    if np.sum(temp == TILE_PATCH) >= MIN_PATCH_TILES:
        patch = temp
        print(f"✅ Patch generated after {attempt+1} attempt(s) with {np.sum(patch == TILE_PATCH)} tiles.")
        break
    attempt += 1
else:
    print("❌ Failed to generate a valid patch after max attempts.")

# --- COMBINE MAPS ---
combined = np.where(patch == TILE_PATCH, TILE_PATCH, base)

# --- PRINT SEEDS AND MATRICES ---
print("Seed (Base):", SEED_BASE)
print("Seed (Patch):", SEED_PATCH + attempt)
print("\nBase Map (0 = empty, 1 = terrain):")
print(base)
print("\nPatch Map (0 = empty, 2 = patch):")
print(patch)
print("\nCombined Map (0 = empty, 1 = base, 2 = patch):")
print(combined)

# --- VISUALIZATION ---
cmap = plt.matplotlib.colors.ListedColormap(["white", "lightgreen", "orange"])
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

axs[0].imshow(base, cmap=cmap, origin='upper')
axs[0].set_title("Base Map (Connected)")

axs[1].imshow(patch, cmap=cmap, origin='upper')
axs[1].set_title("Patch Map (Connected, ≥30 tiles)")

axs[2].imshow(combined, cmap=cmap, origin='upper')
axs[2].set_title("Combined Map")

for ax in axs:
    ax.axis("off")

legend_elements = [
    Patch(facecolor=cmap(0), edgecolor='black', label="0: Empty"),
    Patch(facecolor=cmap(1), edgecolor='black', label="1: Base Terrain"),
    Patch(facecolor=cmap(2), edgecolor='black', label="2: Patch Area"),
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
