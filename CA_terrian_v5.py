import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from collections import deque
import random
import time

# --- SETTINGS ---
USE_FIXED_SEED = False
MAP_WIDTH, MAP_HEIGHT = 40, 30
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

def connect_grass(grid, tile_type=TILE_GRASS, min_width=2):
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
                    if not visited[nx, ny] and grid[nx, ny] == tile_type:
                        visited[nx, ny] = True
                        queue.append((nx, ny))
        return region

    visited = np.zeros_like(grid, dtype=bool)
    regions = []
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if grid[x, y] == tile_type and not visited[x, y]:
                regions.append(flood_fill(x, y, visited))

    if not regions:
        return grid

    main = regions[0]
    for region in regions[1:]:
        (x1, y1), (x2, y2) = min(((a, b) for a in main for b in region),
                                 key=lambda p: abs(p[0][0]-p[1][0]) + abs(p[0][1]-p[1][1]))
        for dx in range(min_width):
            for y in range(min(y1, y2), max(y1, y2)+1):
                grid[min(x1 + dx, MAP_HEIGHT-1), y] = tile_type
            for x in range(min(x1, x2), max(x1, x2)+1):
                grid[x, min(y2 + dx, MAP_WIDTH-1)] = tile_type
        main.update(region)
    return grid

# --- COHERENT WATER PATCHES ---
def generate_water_overlay(terrain, patch_prob=0.03):
    water = np.zeros_like(terrain)
    patch_shapes = [
        [(0,0), (0,1), (1,0), (1,1)],  # 2x2 block
        [(0,0), (0,1), (0,2), (1,1)],  # cross 3x3 center
        [(0,0), (0,1), (1,0), (1,1), (2,1)]  # L-shaped 3x3
    ]
    for x in range(MAP_HEIGHT - 2):
        for y in range(MAP_WIDTH - 2):
            if terrain[x, y] == TILE_GRASS and random.random() < patch_prob:
                shape = random.choice(patch_shapes)
                can_place = all(
                    0 <= x+dx < MAP_HEIGHT and 0 <= y+dy < MAP_WIDTH and
                    terrain[x+dx, y+dy] == TILE_GRASS and water[x+dx, y+dy] == 0
                    for dx, dy in shape
                )
                if can_place:
                    for dx, dy in shape:
                        water[x+dx, y+dy] = TILE_WATER
    return water

# --- OBJECT HELPERS ---
def is_too_dense(layer, x, y, tile_type, radius):
    for dx in range(-radius, radius+1):
        for dy in range(-radius, radius+1):
            if abs(dx)+abs(dy) > radius: continue
            nx, ny = x+dx, y+dy
            if 0 <= nx < MAP_HEIGHT and 0 <= ny < MAP_WIDTH:
                if layer[nx, ny] == tile_type:
                    return True
    return False

def is_far_enough(grid, x, y, obj, min_dist):
    for dx in range(-min_dist, min_dist + 1):
        for dy in range(-min_dist, min_dist + 1):
            if abs(dx) + abs(dy) > min_dist: continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                if grid[nx, ny] == obj:
                    return False
    return True

# --- SCENE + INTERACTIVE LAYERS ---
def generate_scene_layer(terrain, water):
    layer = np.full_like(terrain, TILE_EMPTY)
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if terrain[x, y] == TILE_GRASS and water[x, y] != TILE_WATER:
                r = random.random()
                if r < 0.05 and not is_too_dense(layer, x, y, TILE_TREE, 2):
                    layer[x, y] = TILE_TREE
                elif r < 0.08 and not is_too_dense(layer, x, y, TILE_ROCK, 2):
                    layer[x, y] = TILE_ROCK
    return layer

def generate_interactive_layer(terrain, scene):
    layer = np.full_like(terrain, TILE_EMPTY)
    object_probs = {
        TILE_CHEST: 0.02,
        TILE_DOOR: 0.015,
        TILE_KEY: 0.015,
        TILE_POTION: 0.02
    }
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if terrain[x, y] == TILE_GRASS and scene[x, y] == TILE_EMPTY:
                r = random.random()
                cumulative = 0
                for obj, prob in object_probs.items():
                    cumulative += prob
                    if r < cumulative and is_far_enough(layer, x, y, obj, 3):
                        layer[x, y] = obj
                        break
    return layer

# --- PIPELINE EXECUTION ---
terrain = initialize_terrain()
terrain = smooth_terrain(terrain)
terrain = connect_grass(terrain)

water = generate_water_overlay(terrain)
scene = generate_scene_layer(terrain, water)
interactives = generate_interactive_layer(terrain, scene)

# --- COMBINE FOR DISPLAY ---
final = np.where(interactives != TILE_EMPTY, interactives,
         np.where(scene != TILE_EMPTY, scene,
         np.where(water == TILE_WATER, TILE_WATER, terrain)))

# --- VISUALIZATION ---
cmap = ListedColormap([
    "white",       # 0
    "green",       # 1
    "blue",        # 2
    "saddlebrown", # 3
    "gray",        # 4
    "gold",        # 5
    "darkred",     # 6
    "yellow",      # 7
    "violet"       # 8
])
bounds = list(range(len(TILE_LABELS)+1))
norm = BoundaryNorm(bounds, cmap.N)

plt.figure(figsize=(12, 9))
plt.imshow(final, cmap=cmap, norm=norm)
plt.title("Natural Water Patches + All Layers (Connected Grass)")
plt.axis("off")
legend_elements = [Patch(facecolor=cmap(i), edgecolor='black', label=TILE_LABELS[i]) for i in TILE_LABELS]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
