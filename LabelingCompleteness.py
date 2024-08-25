import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# tile_name = "tiles_"
# format = ".png"
# Similarity_threshold = 0.671875
root_folder = "Data/GameTile/small_segment_recursive/"
tile_path = "002_001/"
# out_file = out_path+"all_tilesets.json"


class ImageLabelingApp:
    def __init__(self, master, image_folder):
        self.master = master
        self.image_folder = image_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]
        self.current_image_index = 0
        self.selected_labels = []
        self.labels = {f: [] for f in self.image_files}
        self.create_output_folders()

        self.label_var = tk.StringVar()
        self.label_var.set("Labels: None")

        self.create_widgets()
        self.show_image()

    def create_widgets(self):
        self.image_label = tk.Label(self.master)
        self.image_label.pack()

        self.label_display = tk.Label(self.master, textvariable=self.label_var)
        self.label_display.pack()

        self.button_complete = tk.Button(self.master, text="Complete", command=lambda: self.label_image("complete"))
        self.button_complete.pack(side=tk.LEFT)

        self.button_part = tk.Button(self.master, text="Part", command=lambda: self.label_image("part"))
        self.button_part.pack(side=tk.LEFT)

        self.button_texture = tk.Button(self.master, text="Texture", command=lambda: self.label_image("texture"))
        self.button_texture.pack(side=tk.LEFT)

        self.button_clear = tk.Button(self.master, text="Clear", command=self.clear_labels)
        self.button_clear.pack(side=tk.LEFT)        

        self.button_next = tk.Button(self.master, text="Next", command=self.next_image)
        self.button_next.pack(side=tk.RIGHT)

    def update_label_display(self):
        image_file = self.image_files[self.current_image_index]
        current_labels = ', '.join( self.labels[image_file])
        self.label_var.set(f"Labels: {current_labels if current_labels else 'None'}")

    def clear_labels(self):
        image_file = self.image_files[self.current_image_index]
        self.labels[image_file].clear()
        self.update_label_display()

    def show_image(self):
        if self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            image = Image.open(image_path)
            image = image.resize((224, 224))  # Resize for display
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            current_labels = ', '.join(self.labels.get(self.image_files[self.current_image_index], []))
            self.label_var.set(f"Labels: {current_labels if current_labels else 'None'}")

    def label_image(self, label):
        image_file = self.image_files[self.current_image_index]
        if label not in self.labels[image_file]:
            self.labels[image_file].append(label)
        current_labels = ', '.join(self.labels[image_file])
        self.label_var.set(f"Labels: {current_labels}")
        self.copy_labeled_image(image_file)

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.image_files):
            self.current_image_index = 0
        self.show_image()

    def copy_labeled_image(self, image_file):
        source_path = os.path.join(self.image_folder, image_file)
        labels = self.labels[image_file]
        prefix = modify_folder_name(tile_path)

        for label in labels:
            if 'texture' in labels:
                combined_label = f"{label}_texture"
                dest_folder = os.path.join(root_folder, f"{prefix}_{combined_label}")
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, image_file)
                shutil.copy(source_path, dest_path)
            dest_folder = os.path.join(root_folder, f"{prefix}_{label}")
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = os.path.join(dest_folder, image_file)
            shutil.copy(source_path, dest_path)

    def save_results(self):
        prefix = modify_folder_name(tile_path)
        with open(os.path.join(root_folder, prefix+'_labels.json'), 'w') as f:
            json.dump(self.labels, f, indent=4)

    def create_output_folders(self):
        prefix = modify_folder_name(tile_path)
        for label in ["complete", "part", "texture"]:
            os.makedirs(os.path.join(root_folder, f"{prefix}_{label}"), exist_ok=True)
        for combined_label in ["complete_texture", "part_texture"]:
            os.makedirs(os.path.join(root_folder, f"{prefix}_{combined_label}"), exist_ok=True)

def modify_folder_name(folder_path):
    """
    Modify a folder name string by removing the trailing slash and keeping the last part of the path.

    Args:
    folder_path (str): The original folder path.

    Returns:
    str: The modified folder name.
    """
    # Remove the trailing slash if it exists
    folder_path = folder_path.rstrip('/')

    # Split the path and get the last part
    modified_name = os.path.basename(folder_path)

    return modified_name


def main():
    root = tk.Tk()
    image_folder = root_folder+tile_path  # Set your folder path here
    if not os.path.exists(image_folder):
        print("The specified folder does not exist. Exiting...")
        return
    app = ImageLabelingApp(root, image_folder)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_results(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()