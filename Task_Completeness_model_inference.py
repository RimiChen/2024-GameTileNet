import torch
from torchvision import models, transforms
from PIL import Image

# === Load model
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = torch.nn.Linear(model.last_channel, 2)
model.load_state_dict(torch.load("Data/GameTile/best_completeness_model.pth"))
model.eval()

# === Inference example
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

image_path = "path_to_some_tile.png"
image = Image.open(image_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0)  # shape: [1, 3, 64, 64]

with torch.no_grad():
    output = model(input_tensor)
    _, predicted = output.max(1)
    label = predicted.item()

print(f"Predicted label: {'complete' if label == 1 else 'part'}")
