import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from collections import deque
import random
import time

# --- SETTINGS ---
USE_FIXED_SEED = True
MAP_WIDTH, MAP_HEIGHT = 20, 15
SEED = 42 if USE_FIXED_SEED else int(time.time())
np.random.seed(SEED)
random.seed(SEED)
print(f"[Seed Mode] Using seed: {SEED}")

# --- TILE DEFINITIONS ---
TILE_EMPTY = 0
TILE_GRASS = 1
TILE_WATER = 2
TILE_TREE = 3
TILE_ROCK = 4
TILE_CHEST = 5
TILE_DOOR = 6
TILE_KEY = 7
TILE_POTION = 8

TILE_LABELS = {
    TILE_EMPTY: "Empty",
    TILE_GRASS: "Grass",
    TILE_WATER: "Water",
    TILE_TREE: "Tree",
    TILE_ROCK: "Rock",
    TILE_CHEST: "Chest",
    TILE_DOOR: "Door",
    TILE_KEY: "Key",
    TILE_POTION: "Potion"
}

# --- UTILS ---
def initialize_terrain(prob=0.6):
    return np.random.choice([TILE_EMPTY, TILE_GRASS], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

def smooth_terrain(grid, iterations=4):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                neighbors = sum(
                    0 <= x+dx < MAP_HEIGHT and 0 <= y+dy < MAP_WIDTH and grid[x+dx, y+dy] == TILE_GRASS
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = TILE_GRASS if neighbors > 4 else TILE_EMPTY
        grid = new_grid
    return grid

def connect_grass(grid):
    def flood_fill(x, y, visited):
        queue = deque([(x, y)])
        region = set()
        visited[x, y] = True
        while queue:
            cx, cy = queue.popleft()
            region.add((cx, cy))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < MAP_HEIGHT and 0 <= ny < MAP_WIDTH:
                    if not visited[nx, ny] and grid[nx, ny] == TILE_GRASS:
                        visited[nx, ny] = True
                        queue.append((nx, ny))
        return region

    visited = np.zeros_like(grid, dtype=bool)
    regions = []
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if grid[x, y] == TILE_GRASS and not visited[x, y]:
                regions.append(flood_fill(x, y, visited))

    if not regions:
        return grid

    main = regions[0]
    for region in regions[1:]:
        (x1, y1), (x2, y2) = min(((a, b) for a in main for b in region),
                                 key=lambda p: abs(p[0][0]-p[1][0]) + abs(p[0][1]-p[1][1]))
        for y in range(min(y1, y2), max(y1, y2)+1):
            grid[x1, y] = TILE_GRASS
        for x in range(min(x1, x2), max(x1, x2)+1):
            grid[x, y2] = TILE_GRASS
        main.update(region)
    return grid

# --- COHERENT WATER PATCH ---
def generate_water_overlay(terrain, patch_prob=0.05):
    water = np.zeros_like(terrain)
    patch_shapes = [[(0,0), (0,1), (1,0), (1,1)],  # 2x2
                    [(0,0), (0,1), (1,1), (1,0), (2,1)],  # L shape
                    [(0,0), (0,1), (0,2), (1,1), (2,1)]]  # plus

    for x in range(MAP_HEIGHT - 2):
        for y in range(MAP_WIDTH - 2):
            if terrain[x, y] == TILE_GRASS and random.random() < patch_prob:
                shape = random.choice(patch_shapes)
                if all(terrain[x+dx, y+dy] == TILE_GRASS and water[x+dx, y+dy] == 0 for dx, dy in shape):
                    for dx, dy in shape:
                        water[x+dx, y+dy] = TILE_WATER
    # guarantee one patch
    if not np.any(water == TILE_WATER):
        for dx, dy in [(0,0), (0,1), (1,0), (1,1)]:
            water[dx, dy] = TILE_WATER
    return water

# --- PLACEMENT HELPERS ---
def place_first_if_missing(layer, terrain, water, tile_id):
    if np.count_nonzero(layer == tile_id) == 0:
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                if terrain[x, y] == TILE_GRASS and water[x, y] != TILE_WATER and layer[x, y] == TILE_EMPTY:
                    layer[x, y] = tile_id
                    return layer
    return layer

def is_far_enough(layer, x, y, tile_id, min_dist):
    for dx in range(-min_dist, min_dist+1):
        for dy in range(-min_dist, min_dist+1):
            nx, ny = x+dx, y+dy
            if abs(dx)+abs(dy) > min_dist: continue
            if 0 <= nx < MAP_HEIGHT and 0 <= ny < MAP_WIDTH:
                if layer[nx, ny] == tile_id:
                    return False
    return True

# --- LAYER GENERATION ---
def generate_scene_layer(terrain, water):
    layer = np.full_like(terrain, TILE_EMPTY)
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if terrain[x, y] == TILE_GRASS and water[x, y] != TILE_WATER:
                r = random.random()
                if r < 0.05:
                    layer[x, y] = TILE_TREE
                elif r < 0.08:
                    layer[x, y] = TILE_ROCK
    layer = place_first_if_missing(layer, terrain, water, TILE_TREE)
    layer = place_first_if_missing(layer, terrain, water, TILE_ROCK)
    return layer

def generate_interactive_layer(terrain, scene):
    layer = np.full_like(terrain, TILE_EMPTY)
    objects = [TILE_CHEST, TILE_DOOR, TILE_KEY, TILE_POTION]
    for obj in objects:
        placed = False
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                if terrain[x, y] == TILE_GRASS and scene[x, y] == TILE_EMPTY and layer[x, y] == TILE_EMPTY:
                    if is_far_enough(layer, x, y, obj, 2):
                        layer[x, y] = obj
                        placed = True
                        break
            if placed:
                break
    return layer

# --- PIPELINE ---
terrain = initialize_terrain()
terrain = smooth_terrain(terrain)
terrain = connect_grass(terrain)
water = generate_water_overlay(terrain)
scene = generate_scene_layer(terrain, water)
interactives = generate_interactive_layer(terrain, scene)

# --- FINAL DISPLAY ---
final = np.where(interactives != TILE_EMPTY, interactives,
         np.where(scene != TILE_EMPTY, scene,
         np.where(water == TILE_WATER, TILE_WATER, terrain)))

cmap = ListedColormap([
    "white", "green", "blue", "saddlebrown", "gray",
    "gold", "darkred", "yellow", "violet"
])
bounds = list(range(len(TILE_LABELS)+1))
norm = BoundaryNorm(bounds, cmap.N)

plt.figure(figsize=(10, 7))
plt.imshow(final, cmap=cmap, norm=norm)
plt.title("Compact Map with Guaranteed Elements")
plt.axis("off")
legend_elements = [Patch(facecolor=cmap(i), edgecolor='black', label=TILE_LABELS[i]) for i in TILE_LABELS]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
