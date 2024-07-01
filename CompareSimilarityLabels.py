import os
import json

human_folder = "Data/GameTile/small_SimilarityLabel_verify/" 
model_folder = "Data/GameTile/small_SimilarityLabel_auto/"
out_path = "Data/GameTile/Json/"

def load_json_file(file_path):
    """
    Load data from a JSON file.

    Parameters:
    file_path (str): Path to the JSON file.

    Returns:
    list: A list of dictionaries containing the data from the JSON file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def compare_connections(human_labels, model_labels):
    """
    Compare the `connected` values between human labels and model labels.

    Parameters:
    human_labels (list): List of dictionaries containing human labels.
    model_labels (list): List of dictionaries containing model labels.

    Returns:
    dict: A dictionary containing the comparison results.
    """
    comparison_results = {
        "total": 0,
        "matching": 0,
        "non_matching": 0,
        "detailed_comparison": []
    }
    
    human_dict = { (pair['image1'], pair['image2']): pair['connected'] for pair in human_labels }
    model_dict = { (pair['image1'], pair['image2']): pair['connected'] for pair in model_labels }

    for key in human_dict:
        comparison_results["total"] += 1
        if human_dict[key] == model_dict.get(key, None):
            comparison_results["matching"] += 1
        else:
            comparison_results["non_matching"] += 1
        comparison_results["detailed_comparison"].append({
            "image_pair": key,
            "human_connected": human_dict[key],
            "model_connected": model_dict.get(key, None)
        })

    return comparison_results

def process_comparison(human_folder, model_folder, output_path):
    """
    Process and compare results from two folders and save the comparison results.

    Parameters:
    human_folder (str): Path to the folder containing human label JSON files.
    model_folder (str): Path to the folder containing model output JSON files.
    output_path (str): Path to save the comparison results JSON file.
    """
    all_comparison_results = {}

    human_files = [f for f in os.listdir(human_folder) if f.startswith('label_similarity_') and f.endswith('.json')]
    model_files = [f for f in os.listdir(model_folder) if f.startswith('output_image_pairs_') and f.endswith('.json')]

    for human_file in human_files:
        index = human_file.split('_')[-1].split('.')[0]
        model_file = f"output_image_pairs_{index}.json"

        if model_file in model_files:
            human_file_path = os.path.join(human_folder, human_file)
            model_file_path = os.path.join(model_folder, model_file)

            human_labels = load_json_file(human_file_path)
            model_labels = load_json_file(model_file_path)

            comparison_results = compare_connections(human_labels, model_labels)
            all_comparison_results[f"comparison_{index}"] = comparison_results

    with open(output_path, 'w') as output_file:
        json.dump(all_comparison_results, output_file, indent=4)

    print(f"Comparison results saved to {output_path}")

# Example usage
if __name__ == "__main__":
    human_folder = human_folder  # Replace with your human label folder path
    model_folder = model_folder  # Replace with your model output folder path
    output_path = out_path + "similarity_comparison_results.json"  # Replace with your desired output JSON file path

    process_comparison(human_folder, model_folder, output_path)