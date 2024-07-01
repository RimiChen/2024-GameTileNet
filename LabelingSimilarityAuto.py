import os
import json
from CheckTileSimilarity import *

json_path = "Data/GameTile/small_SimilarityLabel_pairs_verify/"
# image_pair_file = json_path + "output_image_pairs_"+str(index)+".json"
# print("source: ", image_pair_file)
out_path = "Data/GameTile/small_SimilarityLabel_auto/"
# out_file = out_path+"label_similarity_"+str(index)+".json"
# print("result: ", out_file)

import os
import json

def load_image_pairs(file_path):
    """
    Load image pairs from a JSON file.

    Parameters:
    file_path (str): Path to the JSON file.

    Returns:
    list: A list of dictionaries containing image pairs.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def calculate_similarity(image1, image2):
    """
    Self-defined function to calculate the similarity between two images.

    Parameters:
    image1 (str): Path to the first image.
    image2 (str): Path to the second image.

    Returns:
    float: Calculated similarity value.
    """
    similarity = checkSimilarity(image1, image2)
    # Implement your similarity calculation logic here
    # This is a placeholder for demonstration purposes
    return similarity

def label_connections(image_pairs, threshold):
    """
    Label the connections based on similarity threshold.

    Parameters:
    image_pairs (list): List of dictionaries containing image pairs.
    threshold (float): The similarity threshold for labeling connections.

    Returns:
    list: A list of dictionaries with the connection labels.
    """
    labeled_pairs = []
    for pair in image_pairs:
        similarity = calculate_similarity(pair['image1'], pair['image2'])
        pair['similarity'] = similarity
        pair['connected'] = bool(similarity >= threshold)  # Ensure conversion to Python bool
        labeled_pairs.append(pair)
    print(labeled_pairs)
    return labeled_pairs

def save_labeled_pairs(labeled_pairs, output_path):
    """
    Save the labeled image pairs to a JSON file.

    Parameters:
    labeled_pairs (list): List of dictionaries containing labeled image pairs.
    output_path (str): Path to save the output JSON file.
    """
    with open(output_path, 'w') as file:
        json.dump(labeled_pairs, file, indent=4)
    print(f"Labeled image pairs saved to {output_path}")

def process_files(input_folder, output_folder, threshold):
    """
    Process all JSON files in the input folder and save the labeled pairs to the output folder.

    Parameters:
    input_folder (str): Path to the folder containing input JSON files.
    output_folder (str): Path to the folder where output JSON files will be saved.
    threshold (float): The similarity threshold for labeling connections.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            image_pairs = load_image_pairs(input_file_path)
            labeled_pairs = label_connections(image_pairs, threshold)
            save_labeled_pairs(labeled_pairs, output_file_path)

# Example usage
if __name__ == "__main__":
    input_folder = json_path  # Replace with your input folder path
    output_folder = out_path  # Replace with your output folder path
    similarity_threshold = 0.671875  # Set your similarity threshold
    # similarity_threshold = 0.9375  # Set your similarity threshold


    process_files(input_folder, output_folder, similarity_threshold)
