import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import deque
import random
import time

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
INITIAL_MAP = 0.75
TILE_EMPTY = 0
TILE_BASE = 1  # Base terrain = 1
USE_FIXED_SEED = True
SEED = 42 if USE_FIXED_SEED else int(time.time())
np.random.seed(SEED)
random.seed(SEED)
print(f"[Seed Mode] Using seed: {SEED}")

# --- Initialize base with random fill ---
def initialize_map(prob=0.65):
    return np.random.choice([TILE_EMPTY, TILE_BASE], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

# --- CA smoothing ---
def smooth_map(grid, tile_type, iterations=4):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                neighbors = sum(
                    0 <= x+dx < grid.shape[0] and 0 <= y+dy < grid.shape[1] and grid[x+dx, y+dy] == tile_type
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1] if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = tile_type if neighbors >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

# --- Keep only largest connected terrain region ---
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

# --- Generate base map ---
base = initialize_map(prob=INITIAL_MAP)
base = smooth_map(base, TILE_BASE, iterations=4)
base = connect_largest_region(base, TILE_BASE)

# --- Visualize ---
cmap = plt.matplotlib.colors.ListedColormap(["white", "lightgreen"])
plt.figure(figsize=(10, 6))
plt.imshow(base, cmap=cmap, origin='upper')
plt.title("Connected Walkable Base Map (0 = Empty, 1 = Terrain)")
plt.axis("off")

legend_elements = [
    Patch(facecolor=cmap(0), edgecolor='black', label="0: Empty"),
    Patch(facecolor=cmap(1), edgecolor='black', label="1: Terrain")
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# --- Output the matrix (0s and 1s) for verification or saving ---
print("Base Map (0 = empty, 1 = terrain):")
print(base)
