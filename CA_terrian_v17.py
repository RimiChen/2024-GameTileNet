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
TILE_BASE = 1
TILE_PATCH = 2

USE_FIXED_SEED = True
SEED_BASE = 42
SEED_PATCH = 1234

BASE_PROB = 0.65
BASE_ITER = 4
PATCH_PROB = 0.50
PATCH_ITER = 2
MIN_PATCH_TILES = 30
MAX_ATTEMPTS = 50

# --- MATERIAL KEYWORDS ---
material_keywords = ["grass", "mud", "dirt", "rock", "sand", "soil", "wood", "stone", "tile", "concrete", "metal", "earth"]

# --- LOAD OBJECT FILE ---
file_path = "StoryFiles/2_object_affordance_langchain.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Select ONE Scene to Process ---
scene = data["per_scene_affordances"][0]
scene_title = scene["scene_title"]
print(f"📘 Processing scene: {scene_title}")

# --- Extract Base Terrain from Suggested Terrain ---
terrain_selection = []
material_counts = Counter()

for obj in scene["objects"]:
    terrain_raw = obj.get("suggested_terrain", "").lower()
    options = [t.strip() for t in terrain_raw.split(",") if t.strip()]
    selected = None
    for opt in options:
        if any(m in opt for m in material_keywords):
            selected = opt
            break
    if not selected:
        material_counts.update(options)
    terrain_selection.append((terrain_raw, selected))

fallback_material = material_counts.most_common(1)[0][0] if material_counts else "grass"
final_terrain_tags = []
for raw, selected in terrain_selection:
    final_terrain_tags.append(selected if selected else fallback_material)

base_name = Counter(final_terrain_tags).most_common(1)[0][0]
print(f"🧱 Base terrain selected: {base_name}")

# --- FUNCTIONS ---
def initialize_map(prob, tile_type, seed):
    np.random.seed(seed)
    return np.random.choice([TILE_EMPTY, tile_type], size=(MAP_HEIGHT, MAP_WIDTH), p=[1 - prob, prob])

def smooth_map(grid, tile_type, iterations):
    for _ in range(iterations):
        new_grid = grid.copy()
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                neighbors = sum(
                    0 <= x+dx < grid.shape[0] and 0 <= y+dy < grid.shape[1] and grid[x+dx, y+dy] == tile_type
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                    if not (dx == 0 and dy == 0)
                )
                new_grid[x, y] = tile_type if neighbors >= 5 else TILE_EMPTY
        grid = new_grid
    return grid

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

# --- Generate Base ---
base_seed = SEED_BASE if USE_FIXED_SEED else int(time.time()) % 100000
base = initialize_map(BASE_PROB, TILE_BASE, base_seed)
base = smooth_map(base, TILE_BASE, BASE_ITER)
base = connect_largest_region(base, TILE_BASE)

# --- Generate Patch ---
patch_id = TILE_PATCH
patch = np.full((MAP_HEIGHT, MAP_WIDTH), TILE_EMPTY)

for attempt in range(MAX_ATTEMPTS):
    temp = initialize_map(PATCH_PROB, patch_id, SEED_PATCH + attempt)
    temp = smooth_map(temp, patch_id, PATCH_ITER)
    temp = connect_largest_region(temp, patch_id)
    if np.sum(temp == patch_id) >= MIN_PATCH_TILES:
        patch = temp
        print(f"✅ Patch for scene '{scene_title}' placed with ID {patch_id}, tiles: {np.sum(patch == patch_id)}")
        break
else:
    print(f"❌ Failed to generate patch for scene '{scene_title}'.")

# --- Combine and Expand Base ---
combined = np.where(patch == patch_id, patch_id, base)
expanded_base = np.where(patch == patch_id, TILE_BASE, base)
expanded_base = connect_largest_region(expanded_base, TILE_BASE)

# --- Visualization ---
cmap = plt.matplotlib.colors.ListedColormap([
    (1,1,1),                          # 0: empty
    (0.6,0.8,0.6),                    # 1: base
    (0.9,0.6,0.3)                     # 2: patch
])
legend = [
    Patch(facecolor=cmap(0), edgecolor='black', label="0: Empty"),
    Patch(facecolor=cmap(1), edgecolor='black', label=f"1: Base ({base_name})"),
    Patch(facecolor=cmap(2), edgecolor='black', label=f"2: Patch ({scene_title})")
]

plt.figure(figsize=(10, 6))
plt.imshow(combined, cmap=cmap, origin='upper')
plt.title("Base + Scene Patch (Connected)")
plt.axis("off")
plt.legend(handles=legend, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# --- Output for Verification ---
print("\n✅ Expanded Base (Connected Walkable Area):")
print(expanded_base)
print("\n🎯 Combined Map (Base + Patch):")
print(combined)
