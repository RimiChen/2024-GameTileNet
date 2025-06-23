import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

# === Load predictions ===
input_path = "Data/GameTile/Models/affordance_predictions.json"
with open(input_path, "r", encoding="utf-8") as f:
    predictions = json.load(f)

print(f"✅ Loaded {len(predictions)} prediction entries")

# === Extract ground truth and predictions ===
true_labels = [entry["true_labels"] for entry in predictions]
predicted_labels = [entry["predicted_labels"] for entry in predictions]

# === Build label binarizer ===
all_labels = sorted(list({label for sublist in true_labels + predicted_labels for label in sublist}))
mlb = MultiLabelBinarizer(classes=all_labels)
Y_true = mlb.fit_transform(true_labels)
Y_pred = mlb.transform(predicted_labels)
label_names = mlb.classes_

# === Compute and print classification report ===
print("\n=== Multi-label Classification Report ===")
report_dict = classification_report(Y_true, Y_pred, target_names=label_names, output_dict=True, zero_division=0)
print(classification_report(Y_true, Y_pred, target_names=label_names, zero_division=0))

# === Precision vs Recall Scatter Plot ===
precision, recall, f1, _ = precision_recall_fscore_support(Y_true, Y_pred, zero_division=0)
plt.figure(figsize=(7, 5))
plt.scatter(recall, precision, color="blue")

for i, name in enumerate(label_names):
    plt.annotate(name, (recall[i], precision[i]), fontsize=9)

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision vs Recall per Affordance Label")
plt.grid(True)
plt.tight_layout()
plt.savefig("Data/GameTile/Models/precision_vs_recall.png", dpi=300)
plt.show()

# === Optional: LaTeX table output ===
# Uncomment to export LaTeX table
# print("\n\\begin{tabular}{lccc}")
# print("\\toprule")
# print("Label & Precision & Recall & F1-score \\\\ \\midrule")
# for i, name in enumerate(label_names):
#     p, r, f = precision[i], recall[i], f1[i]
#     print(f"{name} & {p:.2f} & {r:.2f} & {f:.2f} \\\\")
# print("\\bottomrule\n\\end{tabular}")
