import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import deque, Counter
import json
import random
import time

# --- SETTINGS ---
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_EMPTY = 0
TILE_BASE = 1  # Level -1 base terrain
TILE_START = 10  # Terrain patches start from here

USE_FIXED_SEED = False
SEED = 42 if USE_FIXED_SEED else int(time.time())
np.random.seed(SEED)
random.seed(SEED)
print(f"[Seed Mode] Using seed: {SEED}")

# --- Load LLM terrain objects ---
with open("1_object_affordance_langchain.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract terrain-labeled objects (affordance_level == 0)
terrain_objects = []
terrain_tokens = []
for scene in data["per_scene_affordances"]:
    for obj in scene["objects"]:
        if obj["affordance_level"] == 0:
            terrain_objects.append(obj["object"])
            for token in obj["suggested_terrain"].lower().split(","):
                terrain_tokens.append(token.strip())

terrain_counter = Counter(terrain_tokens)
base_terrain = terrain_counter.most_common(1)[0][0] if terrain_tokens else "grass"
unique_patch_objects = sorted(set(terrain_objects))
patch_tile_ids = {name: TILE_START + i for i, name in enumerate(unique_patch_objects)}

# --- Generate base terrain ---
def initialize_map(prob=0.65):
    return np.random.choice([TILE_EMPTY, TILE_BASE], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

def smooth_map(grid, iterations=5):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(MAP_HEIGHT):
            for y in range(MAP_WIDTH):
                neighbors = sum(
                    0 <= x+dx < MAP_HEIGHT and 0 <= y+dy < MAP_WIDTH and grid[x+dx, y+dy] == TILE_BASE
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = TILE_BASE if neighbors >= 4 else TILE_EMPTY
        grid = new_grid
    return grid

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
                    if not visited[nx, ny] and grid[nx, ny] == TILE_BASE:
                        visited[nx, ny] = True
                        queue.append((nx, ny))
        return region

    regions = []
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            if grid[x, y] == TILE_BASE and not visited[x, y]:
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
            grid[x1, y] = TILE_BASE
        for x in range(min(x1, x2), max(x1, x2)+1):
            grid[x, y2] = TILE_BASE
        main_region.update(region)
    return grid

# --- Place patch inside base with size ≥30 ---
def place_patch(grid, base_mask, label_tile, patch_size=(30, 40)):
    attempts = 0
    while attempts < 100:
        cx = random.randint(3, MAP_HEIGHT - 4)
        cy = random.randint(3, MAP_WIDTH - 4)
        if base_mask[cx, cy] != TILE_BASE:
            attempts += 1
            continue
        target_size = random.randint(*patch_size)
        count = 0
        queue = deque([(cx, cy)])
        visited = set()
        while queue and count < target_size:
            x, y = queue.popleft()
            if (x, y) in visited or not (0 <= x < MAP_HEIGHT and 0 <= y < MAP_WIDTH):
                continue
            if base_mask[x, y] == TILE_BASE and grid[x, y] == TILE_EMPTY:
                grid[x, y] = label_tile
                count += 1
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    queue.append((x+dx, y+dy))
            visited.add((x, y))
        if count >= target_size // 2:
            break
        attempts += 1

# --- Generate layers ---
base_layer = initialize_map()
base_layer = smooth_map(base_layer)
base_layer = connect_regions(base_layer)

patch_layer = np.full_like(base_layer, TILE_EMPTY)
for obj_name, tile_id in patch_tile_ids.items():
    place_patch(patch_layer, base_layer, tile_id, patch_size=(30, 40))

visual_map = np.where(patch_layer != TILE_EMPTY, patch_layer, base_layer)

# --- Visualize ---
color_palette = [(1, 1, 1)]  # white for empty
color_palette.append((0.8, 0.8, 0.8))  # base terrain
for _ in patch_tile_ids:
    color_palette.append((random.random(), random.random(), random.random()))

max_tile_id = max(patch_tile_ids.values())
while len(color_palette) <= max_tile_id:
    color_palette.append((random.random(), random.random(), random.random()))

cmap = plt.matplotlib.colors.ListedColormap(color_palette)
plt.figure(figsize=(10, 6))
plt.imshow(visual_map, cmap=cmap, origin='upper')
plt.title(f"Base: '{base_terrain}' | Scene Patches ≥30 Tiles")
plt.axis("off")

legend_elements = [
    Patch(facecolor=color_palette[tid], edgecolor='black', label=f"{tid}: {name}")
    for name, tid in patch_tile_ids.items()
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
