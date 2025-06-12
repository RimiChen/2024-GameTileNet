import os
import csv
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms

# === Input directories ===
ROOT_FOLDERS = [
    "Data/GameTile/complete_labels_output_model",
    "Data/GameTile/complete_labels_output_algo_no_reduce"
]
OUTPUT_CSV = "Data/GameTile/tile_classification_dataset.csv"

def collect_image_paths():
    rows = []
    for root in ROOT_FOLDERS:
        for label_name, label_value in [("complete", 1), ("part", 0)]:
            label_folder = os.path.join(root, label_name)
            if not os.path.isdir(label_folder):
                continue

            for subfolder in os.listdir(label_folder):
                subfolder_path = os.path.join(label_folder, subfolder)
                if not os.path.isdir(subfolder_path):
                    continue

                for file in os.listdir(subfolder_path):
                    if file.lower().endswith(".png"):
                        image_path = os.path.join(subfolder_path, file)
                        rows.append((image_path, label_value))

    print(f"Collected {len(rows)} labeled tiles.")
    return rows

def save_to_csv(rows, output_path):
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "label"])
        writer.writerows(rows)
    print(f"Saved dataset to: {output_path}")

# === PyTorch Dataset ===
class TileDataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data = []
        with open(csv_file, "r") as f:
            next(f)  # skip header
            for line in f:
                path, label = line.strip().split(",")
                self.data.append((path, int(label)))

        self.transform = transform or transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image_path, label = self.data[idx]
        image = Image.open(image_path).convert("RGB")
        return self.transform(image), label

# === Run everything ===
if __name__ == "__main__":
    data_rows = collect_image_paths()
    save_to_csv(data_rows, OUTPUT_CSV)

    # Optional example:
    # from torch.utils.data import DataLoader
    # dataset = TileDataset(OUTPUT_CSV)
    # loader = DataLoader(dataset, batch_size=32, shuffle=True)
