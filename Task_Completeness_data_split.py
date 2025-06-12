import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_CSV = "Data/GameTile/tile_classification_dataset.csv"

def split_csv(csv_path):
    df = pd.read_csv(csv_path)

    train_val, test = train_test_split(df, test_size=0.1, stratify=df['label'], random_state=42)
    train, val = train_test_split(train_val, test_size=0.1111, stratify=train_val['label'], random_state=42)
    # 0.1111 * 0.9 ≈ 0.1

    train.to_csv("Data/GameTile/completeness_train.csv", index=False)
    val.to_csv("Data/GameTile/completeness_val.csv", index=False)
    test.to_csv("Data/GameTile/completeness_test.csv", index=False)

    print(f"Saved: train.csv ({len(train)}), val.csv ({len(val)}), test.csv ({len(test)})")

if __name__ == "__main__":
    split_csv(INPUT_CSV)
