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
TILE_TERRAIN = 1  # Assigned dynamically
USE_FIXED_SEED = True
SEED = 42 if USE_FIXED_SEED else int(time.time())
np.random.seed(SEED)
random.seed(SEED)
print(f"[Seed Mode] Using seed: {SEED}")

# --- Load affordance JSON ---
with open("2_object_affordance_langchain.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Base terrain materials we recognize ---
# BASE_MATERIALS = {
#     "grass", "mud", "stone", "dirt", "urban", "concrete", "asphalt", "sand", "soil", "wood", "tile", "floor", "ground"
# }

# # --- Extract level-0 terrain labels ---
# terrain_raw = []
# for scene in data["per_scene_affordances"]:
#     for obj in scene["objects"]:
#         if obj["affordance_level"] == 0:
#             terrain_raw.append(obj["suggested_terrain"].strip().lower())

# terrain_counter = Counter(t for t in terrain_raw if t != "any")

# # --- Choose best matching base ground ---
# base_terrain = None
# for terrain, _ in terrain_counter.most_common():
#     if any(mat in terrain for mat in BASE_MATERIALS):
#         base_terrain = terrain
#         break

# if not base_terrain:
#     base_terrain = "grass"
#     print("⚠️ No preferred base ground found. Defaulting to 'grass'.")

# print(f"🟩 Using base terrain: '{base_terrain}'")
# Split and filter terrain suggestions
BASE_MATERIALS = {
    "grass", "mud", "stone", "dirt", "urban", "concrete", "asphalt", "sand", "soil", "wood", "tile", "floor", "ground"
}

terrain_tokens = []
for scene in data["per_scene_affordances"]:
    for obj in scene["objects"]:
        if obj["affordance_level"] == 0:
            for token in obj["suggested_terrain"].lower().split(","):
                token = token.strip()
                if token in BASE_MATERIALS:
                    terrain_tokens.append(token)

terrain_counter = Counter(terrain_tokens)
base_terrain = terrain_counter.most_common(1)[0][0] if terrain_tokens else "grass"



# --- Cellular Automata functions ---
def initialize_map(prob=0.55):
    return np.random.choice([TILE_EMPTY, TILE_TERRAIN], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

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

# --- Generate Terrain ---
terrain = initialize_map()
terrain = smooth_map(terrain)
terrain = connect_regions(terrain)

# --- Updated Visualize: Only Show Chosen Terrain Label ---
cmap = plt.get_cmap("Greens")
plt.figure(figsize=(10, 6))
plt.imshow(terrain, cmap=cmap, origin='upper')
plt.title(f"Connected Walkable Terrain Map: '{base_terrain}'")
plt.axis("off")

legend_elements = [
    Patch(facecolor=cmap(0.9), edgecolor='black', label=f"{TILE_TERRAIN}: {base_terrain.title()}")
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()