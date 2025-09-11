import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from collections import defaultdict
import argparse

# ---- NEW: CLI for min-count (default 0 = no filtering) ----
parser = argparse.ArgumentParser()
parser.add_argument("--min-count", type=int, default=4, help="minimum group frequency to keep")
args = parser.parse_args()
MIN_COUNT = max(0, args.min_count)

# === Paths ===
group_file = 'Data/GameTile/group_supercategories.xlsx'
# label_file = 'Data/GameTile/complete_author_json/manual_group_labels.json'
label_file = 'Data/GameTile/SemanticLabels/author_labeled_1_manual_group_labels.json'
json_stat_output = 'Data/GameTile/group_supercategory_statistics.json'

# === Load Mappings ===
df_map = pd.read_excel(group_file)
group_to_super = dict(zip(df_map.iloc[:, 1], df_map.iloc[:, 0]))  # group : supercategory

with open(label_file, 'r', encoding='utf-8') as f:
    label_data = json.load(f)

# ---- NEW: robust iterator for dict or list ----
entries = label_data.values() if isinstance(label_data, dict) else label_data

# === Count Group Occurrences ===
group_counts = defaultdict(int)
group_to_paths = defaultdict(list)

for entry in entries:
    for group in entry.get("selected_group_tokens", []):
        group_counts[group] += 1
        group_to_paths[group].append(entry)

# ---- NEW: apply min-count filter (non-destructive copy) ----
filtered_group_counts = {g: c for g, c in group_counts.items() if c >= MIN_COUNT} if MIN_COUNT > 0 else dict(group_counts)

# === Aggregate Supercategory Counts (from filtered groups) ===
super_counts = defaultdict(int)
group_super_pairs = []
for group, count in filtered_group_counts.items():
    supercat = group_to_super.get(group, "Unknown")
    super_counts[supercat] += count
    group_super_pairs.append((group, count, supercat))

# === Save JSON Stats ===
json_out = {
    "supercategory_counts": dict(super_counts),
    "group_counts": dict(filtered_group_counts),  # save what was actually plotted
    "group_to_supercategory": group_to_super,
    "min_count": MIN_COUNT,
}
with open(json_stat_output, "w", encoding="utf-8") as f:
    json.dump(json_out, f, indent=2, ensure_ascii=False)

# === Plot 1: Sorted by Count ===
plt.figure(figsize=(20, 3.5))
sorted_groups = sorted(filtered_group_counts.items(), key=lambda x: x[1], reverse=True)
group_names, counts = zip(*sorted_groups) if sorted_groups else ([], [])
plt.bar(group_names, counts, color='steelblue')
plt.xticks(rotation=90, fontsize=9)
if counts:
    plt.ylim(0, max(counts) * 1.15)
plt.title("Group Label Frequency (Sorted by Count)", fontsize=11)  # keep original title text
plt.ylabel("Count", fontsize=9)
plt.xlim(-0.5, len(group_names) - 0.5)  # removes side margins
plt.tight_layout()
plt.show()

# === Plot 2: Grouped by Supercategory (angled labels) ===
group_super_pairs.sort(key=lambda x: (group_to_super.get(x[0], "Unknown"), x[0]))
groups_sorted, counts_sorted, supercats_sorted = zip(*group_super_pairs) if group_super_pairs else ([], [], [])

colors = sns.color_palette("husl", len(set(supercats_sorted)))
supercat_color = {cat: colors[i] for i, cat in enumerate(sorted(set(supercats_sorted)))}
bar_colors = [supercat_color[sc] for sc in supercats_sorted]

fig, ax = plt.subplots(figsize=(20, 3.5))
bars = ax.bar(groups_sorted, counts_sorted, color=bar_colors)
ax.set_xticks(range(len(groups_sorted)))
ax.set_xticklabels(groups_sorted, rotation=90, fontsize=6)
ax.set_ylabel("Count", fontsize=9)
ax.set_title("Group Labels Grouped by Supercategory", fontsize=11)
if counts_sorted:
    ax.set_ylim(0, max(counts_sorted) * 1.25)
ax.set_xlim(-0.5, len(groups_sorted) - 0.5)  # removes side margins

# Supercategory bands + angled labels (unchanged style)
supercat_positions = defaultdict(list)
for i, sc in enumerate(supercats_sorted):
    supercat_positions[sc].append(i)

for sc, indices in supercat_positions.items():
    if not indices:
        continue
    start = min(indices) - 0.5
    end = max(indices) + 0.5
    mid = sum(indices) / len(indices)
    max_height = max([counts_sorted[i] for i in indices]) if counts_sorted else 0
    height = max_height * 0.4
    ax.axvspan(start, end, color=supercat_color[sc], alpha=0.08)
    ax.text(
        mid, height, sc, ha='center', va='bottom',
        fontsize=10, rotation=45, weight='bold',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, boxstyle='round,pad=0.2'),
        clip_on=True
    )

plt.tight_layout()
plt.show()
