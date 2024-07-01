import os
import json
import numpy as np
import scipy.stats as stats

json_path = "Data/GameTile/small_SimilarityLabel/"
out_path = "Data/GameTile/Json/"


def load_similarity_values(folder_path):
    """
    Load similarity values from JSON files in the specified folder.

    Parameters:
    folder_path (str): Path to the folder containing JSON files.

    Returns:
    list: A list of similarity values for connected image pairs.
    """
    similarity_values = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                data = json.load(file)
                for entry in data:
                    if entry["connected"]:
                        similarity_values.append(entry["similarity"])
    return similarity_values

def calculate_statistics(values):
    """
    Calculate statistical values for the given list of values.

    Parameters:
    values (list): List of numerical values.

    Returns:
    dict: Dictionary containing statistical values.
    """
    statistics = {
        "min": np.min(values),
        "max": np.max(values),
        "mean": np.mean(values),
        "median": np.median(values),
        "std": np.std(values),
        "variance": np.var(values),
        "kurtosis": stats.kurtosis(values),
        "skewness": stats.skew(values)
    }
    return statistics

def remove_outliers(values, num_to_remove):
    """
    Remove the specified number of lowest values from the list.

    Parameters:
    values (list): List of numerical values.
    num_to_remove (int): Number of lowest values to remove.

    Returns:
    list: List of values with the outliers removed.
    """
    sorted_values = sorted(values)
    return sorted_values[num_to_remove:]

def save_statistics_to_json(original_stats, cleaned_stats, output_path):
    """
    Save the statistical results to a JSON file.

    Parameters:
    original_stats (dict): Dictionary containing original statistical values.
    cleaned_stats (dict): Dictionary containing statistical values after removing outliers.
    output_path (str): Path to save the output JSON file.
    """
    results = {
        "original_statistics": original_stats,
        "statistics_after_removing_outliers": cleaned_stats
    }
    with open(output_path, 'w') as file:
        json.dump(results, file, indent=4)
    print(f"Statistics saved to {output_path}")

def main(folder_path, num_outliers_to_remove, output_path):
    similarity_values = load_similarity_values(folder_path)
    
    # Calculate original statistics
    original_stats = calculate_statistics(similarity_values)
    
    # Remove outliers and calculate new statistics
    cleaned_values = remove_outliers(similarity_values, num_outliers_to_remove)
    cleaned_stats = calculate_statistics(cleaned_values)
    
    # Save the results to a JSON file
    save_statistics_to_json(original_stats, cleaned_stats, output_path)

# Example usage
if __name__ == "__main__":
    folder_path = json_path  # Replace with your folder path
    num_outliers_to_remove = 5  # Number of lowest values to remove
    output_path = out_path + "similarity_statistics_results.json"  # Replace with your desired output JSON file path
    
    main(folder_path, num_outliers_to_remove, output_path)