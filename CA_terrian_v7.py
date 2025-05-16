import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import random

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY = 0
TILE_TERRAIN = 1

# --- Initialize Random Terrain ---
def initialize_map(prob=0.55):
    return np.random.choice([TILE_EMPTY, TILE_TERRAIN], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

# --- Smooth via Cellular Automata ---
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

# --- Ensure Terrain is Connected ---
def connect_regions(grid):
    visited = np.zeros_like(grid, dtype=bool)

    def flood_fill(x, y):
        region = set()
        queue = deque([(x, y)])
        visited[x, y] = True
        while queue:
            cx, cy = queue.popleft()
            region.add((cx, cy))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dx, cy + dy
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

    if not regions:
        return grid

    main_region = regions[0]
    for region in regions[1:]:
        (x1, y1), (x2, y2) = min(
            ((a, b) for a in main_region for b in region),
            key=lambda p: abs(p[0][0]-p[1][0]) + abs(p[0][1]-p[1][1])
        )
        for y in range(min(y1, y2), max(y1, y2)+1):
            grid[x1, y] = TILE_TERRAIN
        for x in range(min(x1, x2), max(x1, x2)+1):
            grid[x, y2] = TILE_TERRAIN
        main_region.update(region)

    return grid

# --- Main Pipeline ---
terrain = initialize_map()
terrain = smooth_map(terrain, iterations=4)
terrain = connect_regions(terrain)

# --- Visualize ---
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.imshow(terrain, cmap='Greens', origin='upper')
plt.title("Connected Terrain Map (1 = Terrain)")
plt.axis("off")
plt.show()
