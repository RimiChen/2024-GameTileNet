import os
import json

# json_path = "Data/GameTile/old_dataset/"
# image_folder_name = "001-test"
# image_folder = json_path + image_folder_name+"/"

# out_path = "Data/GameTile/Json/"
# out_file = out_path+"objects_"+image_folder_name+".json"


def list_files_in_folder(folder_path):
    """
    List all files in the specified folder, excluding sub-folders.

    Parameters:
    folder_path (str): Path to the folder to scan for files.

    Returns:
    list: List of file paths.
    """
    file_list = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            file_list.append(entry.path)
    return file_list

def save_file_list_to_json(file_list, json_path):
    """
    Save the list of file paths to a JSON file.

    Parameters:
    file_list (list): List of file paths.
    json_path (str): Path to the JSON file to save the list.
    """
    with open(json_path, 'w') as json_file:
        json.dump(file_list, json_file, indent=4)
    print(f"File list saved to {json_path}")

# Example usage
# if __name__ == "__main__":
#     folder_path = image_folder  # Replace with your folder path
#     json_path = out_file         # Replace with your desired JSON file path

#     file_list = list_files_in_folder(folder_path)
#     save_file_list_to_json(file_list, json_path)