import os
import json
import random

json_path = "Data/GameTile/small_dataset_neighbors/"
image_data_path = "Data/GameTile/small_dataset/"

out_path = "Data/GameTile/Json/"


def load_json_files(parent_folder):
    """
    Load all JSON files from the specified folder and subfolders,
    extracting the folder name from the JSON filename.

    Parameters:
    parent_folder (str): Path to the folder containing JSON files.

    Returns:
    dict: A dictionary with all image data from the JSON files, including their folder names.
    """
    image_data = {}
    for root, _, files in os.walk(parent_folder):
        for filename in files:
            if filename.endswith('.json'):
                # Extract the folder name from the filename
                folder_name = filename.split('_neighbors_info.json')[0]
                with open(os.path.join(root, filename), 'r') as file:
                    data = json.load(file)
                    for key in data:
                        data[key]['folder'] = folder_name
                    image_data.update(data)
    return image_data

def get_random_image_pairs(image_data, num_pairs):
    """
    Get a specified number of random image pairs from the image data.

    Parameters:
    image_data (dict): Dictionary containing image data and their neighbors.
    num_pairs (int): Number of random image pairs to select.

    Returns:
    list: A list of tuples, each containing a pair of image filenames and their folder names.
    """
    pairs = []
    images = list(image_data.keys())
    
    while len(pairs) < num_pairs and images:
        image = random.choice(images)
        neighbors = image_data[image]["neighbors"]
        if neighbors:
            neighbor = random.choice(neighbors)
            folder = image_data[image]["folder"]
            print("folder = ", folder)
            neighbor_folder = image_data[neighbor]["folder"]
            print("neighbor_folder = ", neighbor_folder)
            pairs.append({"image1":image_data_path+folder+"/"+image, "image2":image_data_path+neighbor_folder+"/"+neighbor})
            images.remove(image)  # Optionally remove to avoid reselection
        else:
            images.remove(image)  # Remove images with no neighbors
    
    return pairs

def save_image_pairs(pairs, output_path):
    """
    Save the selected image pairs to a JSON file.

    Parameters:
    pairs (list): List of tuples containing image pairs and their folder names.
    output_path (str): Path to save the output JSON file.
    """
    with open(output_path, 'w') as file:
        json.dump(pairs, file, indent=4)
    print(f"Image pairs saved to {output_path}")

# Example usage
if __name__ == "__main__":
    parent_folder =json_path  # Replace with the path to your parent folder containing subfolders with JSON files
    output_path = out_path+"output_image_pairs"  # Replace with the path to save the output JSON file
    num_pairs = 20  # Specify the number of image pairs you want

    for i in range(10):
        new_out_file = output_path+"_"+str(i)+".json"
        image_data = load_json_files(parent_folder)
        pairs = get_random_image_pairs(image_data, num_pairs)
        save_image_pairs(pairs, new_out_file)