import os
import re
import json


tileset_path = "Data/GameTile/dataset_small/"

def parse_filename(filename):
    """
    Parse the filename to extract the image name and coordinates.

    Parameters:
    filename (str): The filename to parse.

    Returns:
    tuple: (image_name, x, y) if the filename matches the expected pattern, None otherwise.
    """
    pattern = r"(.+)_(-?\d+)_(-?\d+)\.png"
    match = re.match(pattern, filename)
    if match:
        image_name = match.group(1)
        x = int(match.group(2))
        y = int(match.group(3))
        return image_name, x, y
    return None

def find_neighbors(folder_path):
    """
    Find the neighbors for each image in the specified folder.

    Parameters:
    folder_path (str): Path to the folder containing images.

    Returns:
    dict: A dictionary where the keys are filenames and the values are dictionaries with neighbor information.
    """
    neighbors_info = {}
    filenames = [f for f in os.listdir(folder_path) if f.endswith('.png')]

    for filename in filenames:
        parsed = parse_filename(filename)
        if not parsed:
            continue
        image_name, x, y = parsed
        neighbors = []

        neighbor_coords = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        for nx, ny in neighbor_coords:
            neighbor_filename = f"{image_name}_{nx}_{ny}.png"
            if neighbor_filename in filenames:
                neighbors.append(neighbor_filename)

        neighbors_info[filename] = {
            "total_neighbors": len(neighbors),
            "neighbors": neighbors
        }

    return neighbors_info

def save_neighbors_info(neighbors_info, output_path):
    """
    Save the neighbors information to a JSON file.

    Parameters:
    neighbors_info (dict): The neighbors information to save.
    output_path (str): Path to the output JSON file.
    """
    with open(output_path, 'w') as json_file:
        json.dump(neighbors_info, json_file, indent=4)
    print(f"Neighbors information saved to {output_path}")

def process_subfolders(parent_folder):
    """
    Process all subfolders within the specified parent folder to find neighbors for images and save the information to JSON files.

    Parameters:
    parent_folder (str): Path to the parent folder containing subfolders.
    """
    for root, dirs, _ in os.walk(parent_folder):
        for dir_name in dirs:
            
            subfolder_path = os.path.join(root, dir_name)
            # print(get_last_folder_name(subfolder_path))
            
            out_path, last_folder = split_path(subfolder_path)
            neighbor_path = out_path+"_neighbors/"

            if not os.path.exists(neighbor_path):
                os.makedirs(neighbor_path)

            if "black" not in subfolder_path and "white" not in subfolder_path:

                if os.path.isdir(subfolder_path):
                    neighbors_info = find_neighbors(subfolder_path)
                    output_path = os.path.join(neighbor_path, last_folder+'_neighbors_info.json')
                    save_neighbors_info(neighbors_info, output_path)


def split_path(path):
    """
    Split the given path into the directory path and the last folder name.

    Parameters:
    path (str): The path to process.

    Returns:
    tuple: (directory_path, last_folder_name)
    """
    # Normalize the path to remove any trailing slashes and make it consistent
    normalized_path = os.path.normpath(path)
    # Split the path into directory path and last folder name
    directory_path, last_folder_name = os.path.split(normalized_path)
    return directory_path, last_folder_name


# Example usage
if __name__ == "__main__":
    parent_folder = tileset_path   # Replace with your parent folder path

    process_subfolders(parent_folder)