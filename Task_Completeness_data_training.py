import torch
from torch import nn, optim
from torchvision import models
from torchvision.transforms import Compose, Resize, ToTensor
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import matplotlib.pyplot as plt
import csv

class TileDataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data = []
        with open(csv_file, "r") as f:
            next(f)
            for line in f:
                path, label = line.strip().split(",")
                self.data.append((path, int(label)))

        self.transform = transform or Compose([
            Resize((64, 64)),
            ToTensor()
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        path, label = self.data[idx]
        img = Image.open(path).convert("RGB")
        return self.transform(img), label

def evaluate_model(model, loader, device):
    model.eval()
    total, correct = 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            out = model(imgs)
            _, preds = out.max(1)
            total += labels.size(0)
            correct += preds.eq(labels).sum().item()
    return correct / total

def train_model(train_csv, val_csv, test_csv, num_epochs=15, batch_size=32, lr=1e-3, patience=3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    train_loader = DataLoader(TileDataset(train_csv), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TileDataset(val_csv), batch_size=batch_size)
    test_loader = DataLoader(TileDataset(test_csv), batch_size=batch_size)

    model = models.mobilenet_v2(pretrained=True)
    model.classifier[1] = nn.Linear(model.last_channel, 2)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_val_acc = 0
    patience_counter = 0
    train_accs, val_accs = [], []
    train_losses = []

    for epoch in range(num_epochs):
        model.train()
        total, correct, epoch_loss = 0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()

            _, preds = out.max(1)
            total += labels.size(0)
            correct += preds.eq(labels).sum().item()
            epoch_loss += loss.item()

        train_acc = correct / total
        train_loss = epoch_loss / len(train_loader)
        val_acc = evaluate_model(model, val_loader, device)

        train_accs.append(train_acc)
        val_accs.append(val_acc)
        train_losses.append(train_loss)

        print(f"Epoch {epoch+1}/{num_epochs} - Train Acc: {train_acc:.3f}, Loss: {train_loss:.4f} → Val Acc: {val_acc:.3f}")

        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), "Data/GameTile/Completeness_training/best_model.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    # === Test Accuracy ===
    model.load_state_dict(torch.load("Data/GameTile/Completeness_training/best_model.pth"))
    test_acc = evaluate_model(model, test_loader, device)
    print(f"\n✅ Test Accuracy: {test_acc:.3f}")

    # === Plot Curves ===
    plt.figure(figsize=(8,5))
    plt.plot(train_accs, label="Train Acc")
    plt.plot(val_accs, label="Val Acc")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Training Curve")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("Data/GameTile/Completeness_training/training_curve.png")
    print("📈 Saved plot to training_curve.png")

if __name__ == "__main__":
    train_model("Data/GameTile/completeness_train.csv", "Data/GameTile/completeness_val.csv", "Data/GameTile/completeness_test.csv", num_epochs=15)
