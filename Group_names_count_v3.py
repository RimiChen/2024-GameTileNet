import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from collections import defaultdict

# === Paths ===
group_file = 'Data/GameTile/group_supercategories.xlsx'
# label_file = 'Data/GameTile/complete_author_json/manual_group_labels.json'
label_file = 'Data/GameTile/SemanticLabels/author_labeled_1_manual_group_labels.json'
json_stat_output = 'Data/GameTile/group_supercategory_statistics.json'

# === Load Mappings ===
df_map = pd.read_excel(group_file)
group_to_super = dict(zip(df_map.iloc[:, 1], df_map.iloc[:, 0]))  # group : supercategory

with open(label_file, 'r') as f:
    label_data = json.load(f)

# === Count Group Occurrences ===
group_counts = defaultdict(int)
group_to_paths = defaultdict(list)

for entry in label_data.values():
    for group in entry.get("selected_group_tokens", []):
        group_counts[group] += 1
        group_to_paths[group].append(entry)

# === Aggregate Supercategory Counts ===
super_counts = defaultdict(int)
group_super_pairs = []

for group, count in group_counts.items():
    supercat = group_to_super.get(group, "Unknown")
    super_counts[supercat] += count
    group_super_pairs.append((group, count, supercat))

# === Save JSON Stats ===
json_out = {
    "supercategory_counts": dict(super_counts),
    "group_counts": dict(group_counts),
    "group_to_supercategory": group_to_super,
}
with open(json_stat_output, "w") as f:
    json.dump(json_out, f, indent=2)

# === Plot 1: Sorted by Count ===
plt.figure(figsize=(18, 2.8))  # Wider + shorter
sorted_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
group_names, counts = zip(*sorted_groups)
plt.bar(group_names, counts, color='steelblue')
plt.xticks(rotation=90, fontsize=5)
plt.ylim(0, max(counts) * 1.15)
plt.title("Group Label Frequency (Sorted by Count)", fontsize=9)
plt.ylabel("Count", fontsize=8)
plt.tight_layout()
plt.show()


# === Plot 2: Grouped by Supercategory ===
group_super_pairs.sort(key=lambda x: (group_to_super.get(x[0], "Unknown"), x[0]))
groups_sorted, counts_sorted, supercats_sorted = zip(*group_super_pairs)

colors = sns.color_palette("husl", len(set(supercats_sorted)))
supercat_color = {cat: colors[i] for i, cat in enumerate(sorted(set(supercats_sorted)))}
bar_colors = [supercat_color[sc] for sc in supercats_sorted]

fig, ax = plt.subplots(figsize=(18, 2.8))

# Plot bars
bars = ax.bar(groups_sorted, counts_sorted, color=bar_colors)
ax.set_xticks(range(len(groups_sorted)))
ax.set_xticklabels(groups_sorted, rotation=90, fontsize=5)
ax.set_ylabel("Count", fontsize=8)
ax.set_title("Group Labels Grouped by Supercategory", fontsize=9)
plt.ylim(0, max(counts_sorted) * 1.15)
plt.subplots_adjust(left=0.04, right=0.98, bottom=0.4, top=0.85)

# Supercategory background regions
supercat_positions = defaultdict(list)
for i, sc in enumerate(supercats_sorted):
    supercat_positions[sc].append(i)

for sc, indices in supercat_positions.items():
    start = min(indices) - 0.5
    end = max(indices) + 0.5
    mid = sum(indices) / len(indices)
    height = max([counts_sorted[i] for i in indices]) * 0.15

    # Draw color band (as translucent rectangle)
    ax.axvspan(start, end, color=supercat_color[sc], alpha=0.1)

    # Label on top of color band
    ax.text(mid, height, sc, ha='center', va='bottom', fontsize=6, weight='bold', rotation=0,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.1'))

plt.show()