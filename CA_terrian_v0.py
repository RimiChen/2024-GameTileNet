import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from collections import deque

# Constants
MAP_WIDTH = 20
MAP_HEIGHT = 20
NUM_ITERATIONS = 4

TILE_EMPTY = 0
TILE_GRASS = 1

# Step 1: Initialize terrain
def initialize_terrain(width, height, grass_prob=0.6):
    np.random.seed(42)
    return np.random.choice([TILE_EMPTY, TILE_GRASS], size=(height, width), p=[1 - grass_prob, grass_prob])

# Step 2: Smooth with cellular automata
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

# Step 3: Ensure full connectivity
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
        # Create horizontal then vertical path
        (x1, y1), (x2, y2) = best_pair
        for y in range(min(y1, y2), max(y1, y2)+1):
            grid[x1, y] = TILE_GRASS
        for x in range(min(x1, x2), max(x1, x2)+1):
            grid[x, y2] = TILE_GRASS
        main_region.update(region)
    return grid

# Step 4: Visualization
def visualize_terrain(grid, title="Connected Terrain Map"):
    cmap = ListedColormap(["white", "green"])
    plt.figure(figsize=(6, 6))
    plt.title(title)
    plt.imshow(grid, cmap=cmap)
    plt.axis("off")
    plt.show()

# Main
def main():
    terrain = initialize_terrain(MAP_WIDTH, MAP_HEIGHT)
    for _ in range(NUM_ITERATIONS):
        terrain = smooth_terrain(terrain)
    regions = find_disconnected_regions(terrain)
    if len(regions) > 1:
        terrain = connect_regions(terrain, regions)
    visualize_terrain(terrain)

if __name__ == "__main__":
    main()
