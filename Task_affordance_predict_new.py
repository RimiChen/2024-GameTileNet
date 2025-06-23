import os
import torch
import torch.nn as nn
import json
from PIL import Image
from torchvision import transforms
import open_clip

# === Configuration ===
IMAGE_DIR = "Data/GameTile/complete_labels_output_algo_no_reduce/upscaled_tiles/realesrgan_x4/003_001_complete"  # Folder with unseen images
MODEL_PATH = "Data/GameTile/Models/affordance_multilabel.pt"
LABELS_PATH = "Data/GameTile/Models/affordance_labels.txt"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
THRESHOLD = 0.5

# === Load CLIP model ===
clip_model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
clip_model = clip_model.to(DEVICE).eval()

# === Load label list ===
with open(LABELS_PATH, "r") as f:
    label_names = [line.strip() for line in f.readlines()]
num_labels = len(label_names)

# === Define classifier ===
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

classifier = MultiLabelMLP(512, num_labels).to(DEVICE)
classifier.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
classifier.eval()

# === Predict function ===
def predict_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        img_feat = clip_model.encode_image(image_tensor)
        logits = classifier(img_feat)
        probs = torch.sigmoid(logits).squeeze().cpu().tolist()
    predicted = [label_names[i] for i, p in enumerate(probs) if p > THRESHOLD]
    return {
        "image": image_path,
        "predicted_labels": predicted,
        "raw_scores": {label_names[i]: round(p, 3) for i, p in enumerate(probs)}
    }

# === Run prediction on all images in folder ===
results = []
for fname in os.listdir(IMAGE_DIR):
    if fname.lower().endswith((".png", ".jpg", ".jpeg")):
        full_path = os.path.join(IMAGE_DIR, fname)
        result = predict_image(full_path)
        results.append(result)
        print(f"[{fname}] → {result['predicted_labels']}")

# === Save predictions ===
output_path = "Data/GameTile/predictions_new.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n✅ Saved predictions to {output_path}")
