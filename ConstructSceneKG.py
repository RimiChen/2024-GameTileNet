import json
import networkx as nx
import matplotlib.pyplot as plt

# === Config ===
INPUT_FILE = "StoryFiles/1_adventure_scene_output_FIXED.json"
OUTPUT_JSON = "StoryFiles/scene_kg_from_relations.json"
ALLOWED_SPATIALS = {"above", "below", "at the right of", "at the left of", "on top of"}

# === Load input data ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# scene_data = raw_data["scenes"] if "scenes" in raw_data else raw_data
scene_data = raw_data.get("scenes", [])
if not scene_data or not isinstance(scene_data[0], dict):
    print("Invalid input: expected a list of scene dictionaries under 'scenes'.")
    exit()

kg_results = []

for scene in scene_data:
    scene_title = scene.get("title", "Untitled")
    triples = []

    for item in scene.get("scene_graph", []):
        subj = item.get("subject")
        obj = item.get("object")
        pred = item.get("predicate")
        spatial = item.get("spatial_mapping", "").lower().strip()

        if subj and obj and pred:
            if spatial in ALLOWED_SPATIALS:
                relation = spatial
            else:
                relation = pred
            triples.append({
                "source": subj,
                "target": obj,
                "relation": relation
            })

    kg_results.append({
        "scene_title": scene_title,
        "triples": triples
    })

# === Save KG JSON ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(kg_results, f, indent=2)

# === Visualize each scene's KG ===
fig, axes = plt.subplots(len(kg_results), 1, figsize=(10, 5 * len(kg_results)))
if len(kg_results) == 1:
    axes = [axes]

for i, scene in enumerate(kg_results):
    G = nx.DiGraph()
    for triple in scene["triples"]:
        G.add_edge(triple["source"], triple["target"], label=triple["relation"])

    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, ax=axes[i], with_labels=True, node_color="lightblue", node_size=2000, font_size=10, edge_color="gray")
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=axes[i], font_color="red")
    axes[i].set_title(f"Scene: {scene['scene_title']}", fontsize=12)

plt.tight_layout()
plt.show()
