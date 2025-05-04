import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from collections import deque
import random
import time


# Constants
MAP_WIDTH = 20
MAP_HEIGHT = 20
NUM_ITERATIONS = 4

# Tile definitions
TILE_EMPTY = 0
TILE_GRASS = 1
TILE_TREE = 2
TILE_ROCK = 3

# --- RANDOM SEED SETTING ---
# Option A: Use a fixed seed for consistent terrain (useful for testing/debugging)
USE_FIXED_SEED = False

if USE_FIXED_SEED:
    seed = 42
    print(f"[Seed Mode] Using fixed seed: {seed}")
else:
    seed = int(time.time())
    print(f"[Seed Mode] Using random seed: {seed}")

np.random.seed(seed)
random.seed(seed)

# --- Terrain Generation Functions ---

def initialize_terrain(width, height, grass_prob=0.6):
    # np.random.seed(42)
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

# --- Scene Object Placement Functions ---

def place_scene_objects(terrain_layer, tree_prob=0.05, rock_prob=0.03):
    scene_layer = np.full_like(terrain_layer, TILE_EMPTY)
    for x in range(terrain_layer.shape[0]):
        for y in range(terrain_layer.shape[1]):
            if terrain_layer[x, y] == TILE_GRASS:
                rand_val = random.random()
                if rand_val < tree_prob:
                    scene_layer[x, y] = TILE_TREE
                elif rand_val < tree_prob + rock_prob:
                    scene_layer[x, y] = TILE_ROCK
    return scene_layer

# --- Visualization Function ---

def visualize_combined(terrain_layer, scene_layer):
    combined_scene = np.where(scene_layer != TILE_EMPTY, scene_layer, terrain_layer)
    cmap = ListedColormap(["white", "green", "saddlebrown", "gray"])
    plt.figure(figsize=(6, 6))
    plt.title("Terrain (Layer 0) + Scene Objects (Layer 1)")
    plt.imshow(combined_scene, cmap=cmap)
    plt.axis("off")
    plt.show()

# --- Main Program ---

def main():
    # Layer 0: Base Terrain
    terrain_layer = initialize_terrain(MAP_WIDTH, MAP_HEIGHT)
    for _ in range(NUM_ITERATIONS):
        terrain_layer = smooth_terrain(terrain_layer)
    regions = find_disconnected_regions(terrain_layer)
    if len(regions) > 1:
        terrain_layer = connect_regions(terrain_layer, regions)

    # Layer 1: Scene Objects
    scene_layer = place_scene_objects(terrain_layer)

    # Visualization
    visualize_combined(terrain_layer, scene_layer)

if __name__ == "__main__":
    main()
