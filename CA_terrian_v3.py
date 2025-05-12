import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from collections import deque
import random
import time

# --- RANDOM SEED SETTING ---
USE_FIXED_SEED = True  # Set to False for random map each run

if USE_FIXED_SEED:
    seed = 42
    print(f"[Seed Mode] Using fixed seed: {seed}")
else:
    seed = int(time.time())
    print(f"[Seed Mode] Using random seed: {seed}")

np.random.seed(seed)
random.seed(seed)

# --- CONSTANTS ---
MAP_WIDTH = 20
MAP_HEIGHT = 20
NUM_ITERATIONS = 4

# Tile IDs
TILE_EMPTY = 0
TILE_GRASS = 1
TILE_TREE = 2
TILE_ROCK = 3
TILE_CHEST = 4
TILE_DOOR = 5
TILE_KEY = 6
TILE_POTION = 7

# --- TERRAIN FUNCTIONS ---
def initialize_terrain(width, height, grass_prob=0.6):
    return np.random.choice([TILE_EMPTY, TILE_GRASS], size=(height, width), p=[1 - grass_prob, grass_prob])

def count_grass_neighbors(grid, x, y):
    total = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                total += (grid[nx, ny] == TILE_GRASS)
    return total

def smooth_terrain(grid):
    new_grid = grid.copy()
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            grass_neighbors = count_grass_neighbors(grid, x, y)
            new_grid[x, y] = TILE_GRASS if grass_neighbors > 4 else TILE_EMPTY
    return new_grid

def flood_fill(grid, start_x, start_y, visited):
    queue = deque([(start_x, start_y)])
    region = set()
    visited[start_x, start_y] = True
    while queue:
        x, y = queue.popleft()
        region.add((x, y))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                if not visited[nx, ny] and grid[nx, ny] == TILE_GRASS:
                    visited[nx, ny] = True
                    queue.append((nx, ny))
    return region

def find_disconnected_regions(grid):
    visited = np.zeros_like(grid, dtype=bool)
    regions = []
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == TILE_GRASS and not visited[x, y]:
                regions.append(flood_fill(grid, x, y, visited))
    return regions

def connect_regions(grid, regions):
    main_region = regions[0]
    for region in regions[1:]:
        min_dist = float('inf')
        best_pair = None
        for (x1, y1) in main_region:
            for (x2, y2) in region:
                d = abs(x1 - x2) + abs(y1 - y2)
                if d < min_dist:
                    min_dist = d
                    best_pair = ((x1, y1), (x2, y2))
        (x1, y1), (x2, y2) = best_pair
        for y in range(min(y1, y2), max(y1, y2)+1):
            grid[x1, y] = TILE_GRASS
        for x in range(min(x1, x2), max(x1, x2)+1):
            grid[x, y2] = TILE_GRASS
        main_region.update(region)
    return grid

# --- LAYER 0: BASE TERRAIN ---
terrain_layer = initialize_terrain(MAP_WIDTH, MAP_HEIGHT)
for _ in range(NUM_ITERATIONS):
    terrain_layer = smooth_terrain(terrain_layer)
regions = find_disconnected_regions(terrain_layer)
if len(regions) > 1:
    terrain_layer = connect_regions(terrain_layer, regions)

# --- LAYER 1: ENVIRONMENTAL OBJECTS (TREES, ROCKS) ---
scene_layer = np.full_like(terrain_layer, TILE_EMPTY)
for x in range(MAP_HEIGHT):
    for y in range(MAP_WIDTH):
        if terrain_layer[x, y] == TILE_GRASS:
            rand_val = random.random()
            if rand_val < 0.05:
                scene_layer[x, y] = TILE_TREE
            elif rand_val < 0.08:
                scene_layer[x, y] = TILE_ROCK

# --- LAYER 2: INTERACTIVE OBJECTS + ITEMS ---
layer2 = np.full_like(terrain_layer, TILE_EMPTY)
for x in range(MAP_HEIGHT):
    for y in range(MAP_WIDTH):
        if terrain_layer[x, y] == TILE_GRASS and scene_layer[x, y] == TILE_EMPTY:
            rand_val = random.random()
            if rand_val < 0.02:
                layer2[x, y] = TILE_CHEST
            elif rand_val < 0.035:
                layer2[x, y] = TILE_DOOR
            elif rand_val < 0.05:
                layer2[x, y] = TILE_KEY
            elif rand_val < 0.07:
                layer2[x, y] = TILE_POTION

# --- FINAL VISUALIZATION ---
final_combined = np.where(layer2 != TILE_EMPTY, layer2,
                   np.where(scene_layer != TILE_EMPTY, scene_layer, terrain_layer))

cmap_all = ListedColormap([
    "white",       # 0 - Empty
    "green",       # 1 - Grass
    "saddlebrown", # 2 - Tree
    "gray",        # 3 - Rock
    "gold",        # 4 - Chest
    "darkred",     # 5 - Door
    "yellow",      # 6 - Key
    "violet"       # 7 - Potion
])

plt.figure(figsize=(6, 6))
plt.title("Layer 0–2: Full Scene with Interactive Objects & Items")
plt.imshow(final_combined, cmap=cmap_all)
plt.axis("off")
plt.show()
