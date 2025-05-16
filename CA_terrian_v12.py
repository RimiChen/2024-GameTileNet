import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import deque
import random
import time

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY = 0
TILE_TERRAIN = 1
USE_FIXED_SEED = True
SEED = 42 if USE_FIXED_SEED else int(time.time())
np.random.seed(SEED)
random.seed(SEED)
print(f"[Seed Mode] Using seed: {SEED}")

# --- INITIALIZE RANDOM MAP ---
def initialize_map(prob=0.80):
    return np.random.choice([TILE_EMPTY, TILE_TERRAIN], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

# --- SMOOTH USING CELLULAR AUTOMATA ---
def smooth_map(grid, iterations=4):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                neighbors = sum(
                    0 <= x+dx < MAP_HEIGHT and 0 <= y+dy < MAP_WIDTH and grid[x+dx, y+dy] == TILE_TERRAIN
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = TILE_TERRAIN if neighbors >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

# --- KEEP LARGEST CONNECTED TERRAIN REGION ---
def connect_largest_region(grid):
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
                if 0 <= nx < MAP_HEIGHT and 0 <= ny < MAP_WIDTH:
                    if not visited[nx, ny] and grid[nx, ny] == TILE_TERRAIN:
                        visited[nx, ny] = True
                        queue.append((nx, ny))
        return region

    regions = []
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if grid[x, y] == TILE_TERRAIN and not visited[x, y]:
                regions.append(flood_fill(x, y))

    # Keep only the largest region
    if not regions:
        return grid

    largest = max(regions, key=len)
    new_grid = np.full_like(grid, TILE_EMPTY)
    for x, y in largest:
        new_grid[x, y] = TILE_TERRAIN
    return new_grid

# --- MAIN PIPELINE ---
grid = initialize_map(prob=0.7)
grid = smooth_map(grid, iterations=4)
grid = connect_largest_region(grid)

# --- VISUALIZATION ---
cmap = plt.get_cmap("Greens")
plt.figure(figsize=(10, 6))
plt.imshow(grid, cmap=cmap, origin='upper')
plt.title("Connected Walkable Terrain (0 = Empty, 1 = Terrain)")
plt.axis("off")

legend_elements = [
    Patch(facecolor=cmap(0.0), edgecolor='black', label="0: Empty"),
    Patch(facecolor=cmap(0.9), edgecolor='black', label="1: Terrain")
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
