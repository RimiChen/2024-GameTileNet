import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Configuration
image_root_folder = "Data/GameTile/complete_labels_output_algo_no_reduce/complete"
output_json_path = "Data/GameTile/object_annotations_recursive.json"
# affordance_options = [
#     "Characters", "Items and Collectibles", "Interactive Object",
#     "Environmental Object", "Obstacle", "Walkable", "Terrain"
# ]
affordance_options = [
    "Characters", "Items and Collectibles", "Interactive Object",
    "Environmental Object", "Terrain"
]

# Load previous annotations if resuming
if os.path.exists(output_json_path):
    with open(output_json_path, "r") as f:
        annotations = json.load(f)
else:
    annotations = {}

# Collect image paths
image_paths = []
for root, _, files in os.walk(image_root_folder):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            full_path = os.path.join(root, file)
            if full_path not in annotations:
                image_paths.append(full_path)
            else:
                image_paths.append(full_path)  # still include to allow navigation

# Annotation GUI
class AnnotationTool:
    def __init__(self, master):
        self.master = master
        master.title("Game Object Annotation Tool")

        self.image_index = 0
        self.label_image = tk.Label(master)
        self.label_image.pack()

        self.entry_detailed = tk.Entry(master, width=50)
        self.entry_group = tk.Entry(master, width=50)
        self.entry_super = tk.Entry(master, width=50)
        self.entry_detailed.pack()
        self.entry_group.pack()
        self.entry_super.pack()

        self.affordance_vars = []
        for label in affordance_options:
            var = tk.IntVar()
            cb = tk.Checkbutton(master, text=label, variable=var)
            cb.pack(anchor="w")
            self.affordance_vars.append((label, var))

        self.button_frame = tk.Frame(master)
        self.button_frame.pack()

        self.button_back = tk.Button(self.button_frame, text="← Back", command=self.prev_image)
        self.button_back.grid(row=0, column=0)

        self.button_save = tk.Button(self.button_frame, text="Save →", command=self.save_annotation)
        self.button_save.grid(row=0, column=1)

        self.load_image()

    def clear_fields(self):
        self.entry_detailed.delete(0, tk.END)
        self.entry_group.delete(0, tk.END)
        self.entry_super.delete(0, tk.END)
        for _, var in self.affordance_vars:
            var.set(0)

    def fill_fields(self, data):
        self.clear_fields()
        self.entry_detailed.insert(0, ", ".join(data.get("detailed_name", [])))
        self.entry_group.insert(0, ", ".join(data.get("group_label", [])))
        self.entry_super.insert(0, ", ".join(data.get("supercategory", [])))
        for label, var in self.affordance_vars:
            var.set(1 if label in data.get("affordance_label", []) else 0)

    def load_image(self):
        if not (0 <= self.image_index < len(image_paths)):
            messagebox.showinfo("Done", "All images annotated.")
            return

        full_path = image_paths[self.image_index]
        rel_path = os.path.relpath(full_path, image_root_folder)

        image = Image.open(full_path).convert("RGBA")
        image.thumbnail((512, 512))
        self.tk_image = ImageTk.PhotoImage(image)

        self.label_image.config(image=self.tk_image)
        self.label_image.image = self.tk_image
        self.current_path = full_path

        # Load annotation if exists
        if full_path in annotations:
            self.fill_fields(annotations[full_path])
        else:
            self.clear_fields()

    def save_annotation(self):
        detailed_names = [x.strip() for x in self.entry_detailed.get().split(",") if x.strip()]
        group_labels = [x.strip() for x in self.entry_group.get().split(",") if x.strip()]
        supercategories = [x.strip() for x in self.entry_super.get().split(",") if x.strip()]
        affordance_labels = [label for label, var in self.affordance_vars if var.get() == 1]

        if not detailed_names or not group_labels:
            messagebox.showwarning("Missing Info", "Detailed name and group label required.")
            return

        annotations[self.current_path] = {
            "detailed_name": detailed_names,
            "group_label": group_labels,
            "supercategory": supercategories,
            "affordance_label": affordance_labels
        }

        with open(output_json_path, "w") as f:
            json.dump(annotations, f, indent=2)

        self.image_index += 1
        self.load_image()

    def prev_image(self):
        if self.image_index > 0:
            self.image_index -= 1
            self.load_image()

root = tk.Tk()
tool = AnnotationTool(root)
root.mainloop()