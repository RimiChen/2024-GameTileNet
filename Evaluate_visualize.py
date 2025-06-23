import json
import matplotlib.pyplot as plt
import os

# Define the input JSON files and their readable names
json_files = {
    "Original (32x32)": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_original.json",
    "Bicubic": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_author_biccubic.json",
    "Real-ESRGAN": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_author_realesrgan_x4.json",
    "SwinIR": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_author_swinir_x4.json",
    "SD Fidelity": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_author_sd_fidelity.json",
    "SD Img2Img": "Data/GameTile/caption_label_match_analysis/summary/summary_caption_label_match_analysis_from_combined_author_sd_img2img.json"
}

# Prepare containers
methods = []
match_types = ["direct", "synonym", "semantic"]
label_types = ["group_labels", "supercategories", "affordance_labels"]
data = {mt: {lt: [] for lt in label_types} for mt in match_types}

# Load real data and convert counts to percentages
for method, filename in json_files.items():
    methods.append(method)
    with open(filename, "r", encoding="utf-8") as f:
        result = json.load(f)
        total_images = result.get("total", {}).get("images", 1)  # avoid divide-by-zero
        for mt in match_types:
            for lt in label_types:
                count = result.get(mt, {}).get(lt, 0)
                percent = (count / total_images) * 100
                data[mt][lt].append(percent)

# Plot
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
colors = {"direct": "steelblue", "synonym": "darkorange", "semantic": "forestgreen"}

for i, lt in enumerate(label_types):
    ax = axes[i]
    bar_width = 0.25
    x = range(len(methods))

    for j, mt in enumerate(match_types):
        offsets = [pos + j * bar_width for pos in x]
        ax.bar(offsets, data[mt][lt], width=bar_width, label=mt.capitalize(), color=colors[mt])

    ax.set_xticks([pos + bar_width for pos in x])
    ax.set_xticklabels(methods, rotation=30)
    ax.set_title(lt.replace("_", " ").title())
    ax.set_ylabel("Match Percentage (%)" if i == 0 else "")
    ax.grid(axis='y', linestyle='--', alpha=0.5)

# Legend below the entire figure
fig.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.05), fontsize=12)
fig.suptitle("Caption–Label Match Percentage Across Upscaling Methods", fontsize=14)
plt.tight_layout(rect=[0, 0.08, 1, 0.95])
plt.show()