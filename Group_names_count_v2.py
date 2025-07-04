import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from collections import defaultdict

# === Paths ===
group_file = 'Data/GameTile/group_supercategories.xlsx'
label_file = 'Data/GameTile/complete_author_json/manual_group_labels.json'
json_stat_output = 'Data/GameTile/group_supercategory_statistics.json'
plot1_output = 'Data/GameTile/plot1_group_counts.png'
plot2_output = 'Data/GameTile/plot2_group_by_supercategory_labeled.png'

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
plt.figure(figsize=(14, 6))
sorted_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
group_names, counts = zip(*sorted_groups)
plt.bar(group_names, counts, color='steelblue')
plt.xticks(rotation=90, fontsize=5)
plt.tight_layout(rect=[0.01, 0.15, 0.99, 0.95])
plt.title("Group Label Frequency (Sorted by Count)")
plt.savefig(plot1_output)
plt.close()

# === Plot 2: Grouped by Supercategory ===
group_super_pairs.sort(key=lambda x: (x[2], x[0]))
groups_sorted, counts_sorted, supercats_sorted = zip(*group_super_pairs)

# Bar colors by supercategory
colors = sns.color_palette("husl", len(set(supercats_sorted)))
supercat_color = {cat: colors[i] for i, cat in enumerate(sorted(set(supercats_sorted)))}
bar_colors = [supercat_color[c] for c in supercats_sorted]

plt.figure(figsize=(16, 6))
bars = plt.bar(groups_sorted, counts_sorted, color=bar_colors)
plt.xticks(rotation=90, fontsize=5)
plt.ylabel("Instance Count")
plt.title("Group Labels Grouped by Supercategory")

# Supercategory segment labeling
supercat_positions = defaultdict(list)
for i, sc in enumerate(supercats_sorted):
    supercat_positions[sc].append(i)

for sc, indices in supercat_positions.items():
    if not indices:
        continue
    mid = sum(indices) / len(indices)
    height = max([counts_sorted[i] for i in indices])
    plt.text(mid, height + 5, sc, ha='center', va='bottom', fontsize=9, weight='bold')

# Legend
handles = [mpatches.Patch(color=supercat_color[cat], label=cat) for cat in sorted(supercat_color)]
plt.legend(handles=handles, loc='upper right', fontsize=7)
plt.tight_layout(rect=[0.01, 0.15, 0.99, 0.90])
plt.savefig(plot2_output)
plt.close()
