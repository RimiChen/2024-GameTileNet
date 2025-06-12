import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Folder settings
input_root_folder = "Data/GameTile/small_Segmenets_model/"
output_root_folder = "Data/GameTile/complete_labels_output_model/"
os.makedirs(output_root_folder, exist_ok=True)


class ImageLabelingApp:
    def __init__(self, master, image_folder, output_folder, prefix):
        self.master = master
        self.image_folder = image_folder
        self.output_folder = output_folder
        self.prefix = prefix
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]
        self.current_image_index = 0
        self.labels = {f: [] for f in self.image_files}
        # self.label_var = tk.StringVar()
        # self.label_var.set("Labels: None")
        # self.create_output_folders()
        # self.create_widgets()
        # self.show_image()
        self.tile_size = 32  # Add this first!
        self.label_var = tk.StringVar()
        self.label_var.set("Labels: None")
        self.create_output_folders()
        self.create_widgets()
        self.show_image()



    def create_widgets(self):
        self.image_label = tk.Label(self.master)
        self.image_label.pack()

        self.label_display = tk.Label(self.master, textvariable=self.label_var)
        self.label_display.pack()

        tk.Button(self.master, text="Complete", command=lambda: self.label_image("complete")).pack(side=tk.LEFT)
        tk.Button(self.master, text="Part", command=lambda: self.label_image("part")).pack(side=tk.LEFT)
        tk.Button(self.master, text="Texture", command=lambda: self.label_image("texture")).pack(side=tk.LEFT)
        tk.Button(self.master, text="Clear", command=self.clear_labels).pack(side=tk.LEFT)
        tk.Button(self.master, text="Next", command=self.next_image).pack(side=tk.RIGHT)

    def update_label_display(self):
        image_file = self.image_files[self.current_image_index]
        current_labels = ', '.join(self.labels[image_file])
        self.label_var.set(f"Labels: {current_labels if current_labels else 'None'}")

    def clear_labels(self):
        image_file = self.image_files[self.current_image_index]
        self.labels[image_file].clear()
        self.update_label_display()

    # def show_image(self):
    #     if self.current_image_index < len(self.image_files):
    #         image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
    #         image = Image.open(image_path).resize((224, 224))
    #         self.photo = ImageTk.PhotoImage(image)  # keep reference
    #         self.image_label.config(image=self.photo)
    #         self.update_label_display()


    def show_image(self):
        if self.current_image_index < len(self.image_files):
            image_file = self.image_files[self.current_image_index]
            image_path = os.path.join(self.image_folder, image_file)
            image = Image.open(image_path)
            
            # Compute size in tiles
            width, height = image.size
            tile_w = width // self.tile_size
            tile_h = height // self.tile_size
            tile_size_text = f"Tile Size: {tile_w}x{tile_h}"

            # Resize for display and show image
            resized = image.resize((224, 224))
            self.photo = ImageTk.PhotoImage(resized)
            self.image_label.config(image=self.photo)

            # Show size info
            self.label_var.set(f"Labels: {', '.join(self.labels[image_file]) or 'None'} | {tile_size_text}")

    def label_image(self, label):
        image_file = self.image_files[self.current_image_index]
        if label not in self.labels[image_file]:
            self.labels[image_file].append(label)
        self.update_label_display()
        self.copy_labeled_image(image_file)

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.image_files):
            self.current_image_index = 0
        self.show_image()

    def copy_labeled_image(self, image_file):
        source_path = os.path.join(self.image_folder, image_file)
        labels = self.labels[image_file]

        for label in labels:
            if 'texture' in labels:
                combined_label = f"{label}_texture"
                self._copy_to(label=combined_label, image_file=image_file, source_path=source_path)
            self._copy_to(label=label, image_file=image_file, source_path=source_path)

    def _copy_to(self, label, image_file, source_path):
        dest_folder = os.path.join(self.output_folder, f"{self.prefix}_{label}")
        os.makedirs(dest_folder, exist_ok=True)
        shutil.copy(source_path, os.path.join(dest_folder, image_file))

    def save_results(self):
        with open(os.path.join(self.output_folder, f'{self.prefix}_labels.json'), 'w') as f:
            json.dump(self.labels, f, indent=4)

    def create_output_folders(self):
        for label in ["complete", "part", "texture"]:
            os.makedirs(os.path.join(self.output_folder, f"{self.prefix}_{label}"), exist_ok=True)
        for combined_label in ["complete_texture", "part_texture"]:
            os.makedirs(os.path.join(self.output_folder, f"{self.prefix}_{combined_label}"), exist_ok=True)

def main():
    root = tk.Tk()
    selected_folder = filedialog.askdirectory(parent=root, title="Select a tile subfolder to label", initialdir=input_root_folder)
    if not selected_folder:
        print("No folder selected. Exiting...")
        root.destroy()
        return

    root.withdraw()  # Hide main window until ready
    prefix = os.path.basename(selected_folder)
    output_folder = output_root_folder

    root.deiconify()  # Show labeling window
    app = ImageLabelingApp(root, selected_folder, output_folder, prefix)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_results(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
