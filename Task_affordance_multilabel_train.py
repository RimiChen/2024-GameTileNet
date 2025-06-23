import os
import json
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from tqdm import tqdm
from torchvision import transforms
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import open_clip

# Load dataset from JSON
with open("Data/GameTile/affordance_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Build label map from all affordance labels
label_set = set()
for entry in data:
    if isinstance(entry["affordance_labels"], list):
        label_set.update(entry["affordance_labels"])

label_list = sorted(label_set)
label2id = {label: idx for idx, label in enumerate(label_list)}
id2label = {idx: label for label, idx in label2id.items()}

# Encode each sample into a label vector
def encode_labels(labels):
    vec = [0] * len(label2id)
    for l in labels:
        if l in label2id:
            vec[label2id[l]] = 1
    return vec

# Prepare image paths and label vectors
image_paths = []
label_vectors = []
for entry in data:
    if not os.path.exists(entry["image_path"]):
        print(f"[Missing] Skipped {entry['image_path']}")
        continue
    image_paths.append(entry["image_path"])
    label_vectors.append(encode_labels(entry["affordance_labels"]))

print(f"✅ Loaded {len(image_paths)} valid images")

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "ViT-B-32"
clip_model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained="openai")
clip_model = clip_model.to(device).eval()

# Extract features from images
features = []
targets = []
print("🔍 Extracting features with CLIP...")
for path, label_vec in tqdm(zip(image_paths, label_vectors), total=len(image_paths)):
    try:
        image = Image.open(path).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = clip_model.encode_image(image_tensor).cpu().squeeze(0)
        features.append(feat)
        targets.append(torch.tensor(label_vec, dtype=torch.float32))
    except Exception as e:
        print(f"⚠️ Failed to process {path}: {e}")

X = torch.stack(features)
Y = torch.stack(targets)

# Train/test split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Define MLP classifier
class MultiLabelMLP(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 512),
            nn.ReLU(),
            nn.Linear(512, out_dim)
        )
    def forward(self, x):
        return self.net(x)

model = MultiLabelMLP(X.shape[1], len(label2id)).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.BCEWithLogitsLoss()

# Training loop
for epoch in range(10):
    model.train()
    total_loss = 0
    for i in range(0, len(X_train), 32):
        xb = X_train[i:i+32].to(device)
        yb = Y_train[i:i+32].to(device)
        optimizer.zero_grad()
        logits = model(xb)
        loss = criterion(logits, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"📚 Epoch {epoch+1}/10 - Loss: {total_loss:.4f}")

# Evaluation
model.eval()
with torch.no_grad():
    logits = model(X_test.to(device)).cpu()
    y_pred = (torch.sigmoid(logits) > 0.5).int()

print("\n=== Multi-label Classification Report ===")
print(classification_report(Y_test, y_pred, target_names=label_list))


# Save prediction results to JSON
results = []
probabilities = torch.sigmoid(logits).numpy()
y_true = Y_test.numpy()

for idx in range(len(probabilities)):
    pred_vector = (probabilities[idx] > 0.5).astype(int)
    result = {
        "image_path": image_paths[X_train.shape[0] + idx],
        "true_labels": [label_list[i] for i, v in enumerate(y_true[idx]) if v == 1],
        "predicted_labels": [label_list[i] for i, v in enumerate(pred_vector) if v == 1],
        "prediction_probs": {label_list[i]: float(probabilities[idx][i]) for i in range(len(label_list))}
    }
    results.append(result)

# Save model and label map
os.makedirs("Data/GameTile/Models", exist_ok=True)

with open("Data/GameTile/Models/affordance_predictions.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✅ Prediction results saved to Data/GameTile/Models/affordance_predictions.json")


torch.save(model.state_dict(), "Data/GameTile/Models/affordance_multilabel.pt")
with open("Data/GameTile/Models/affordance_labels.txt", "w") as f:
    for label in label_list:
        f.write(label + "\n")

print("✅ Model and label map saved.")
