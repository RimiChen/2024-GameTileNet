import os

def count_pngs_in_subfolders(parent_folder):
    total_count = 0
    print(f"Checking folder: {parent_folder}\n")

    for subfolder in sorted(os.listdir(parent_folder)):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            png_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.png')]
            count = len(png_files)
            total_count += count
            print(f"{subfolder}: {count} PNG files")

    print(f"\nTotal PNG files across all subfolders: {total_count}")

# Example usage
# FOLDER = "small_Segmenets_model"
# FOLDER = "bk_small_dataset/No_Reduce_Segments"
# FOLDER = "new_small_segments_recursive"
# FOLDER = "small_dataset/No_Reduce_Tiles"
FOLDER = "complete_labels_output_model/part_texture"


folder_path = "Data/GameTile/"+FOLDER  # Replace with your actual path
count_pngs_in_subfolders(folder_path)
