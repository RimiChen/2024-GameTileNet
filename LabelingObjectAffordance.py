import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# === Configuration ===
image_root_folder = "Data/GameTile/complete_author_cleaned"  # ← Change this if needed
output_json_path = "Data/GameTile/affordance_annotations.json"
affordance_options = [
    "Characters", "Items and Collectibles", "Interactive Object",
    "Environmental Object", "Terrain"
]

# === Load previously saved annotations if available ===
if os.path.exists(output_json_path):
    with open(output_json_path, "r") as f:
        annotations = json.load(f)
else:
    annotations = {}

# === Collect all image file paths ===
image_paths = []
for root, _, files in os.walk(image_root_folder):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(root, file)
            image_paths.append(full_path)

# === Annotation GUI ===
class AffordanceAnnotator:
    def __init__(self, master):
        self.master = master
        master.title("Affordance Annotation Tool")

        self.index = 0
        self.label_image = tk.Label(master)
        self.label_image.pack()

        self.affordance_vars = []
        for label in affordance_options:
            var = tk.IntVar()
            cb = tk.Checkbutton(master, text=label, variable=var)
            cb.pack(anchor="w")
            self.affordance_vars.append((label, var))

        self.btn_frame = tk.Frame(master)
        self.btn_frame.pack()

        self.btn_back = tk.Button(self.btn_frame, text="← Back", command=self.prev_image)
        self.btn_back.grid(row=0, column=0)

        self.btn_next = tk.Button(self.btn_frame, text="Save →", command=self.save_and_next)
        self.btn_next.grid(row=0, column=1)

        self.load_image()

    def clear_selection(self):
        for _, var in self.affordance_vars:
            var.set(0)

    def fill_selection(self, labels):
        for label, var in self.affordance_vars:
            var.set(1 if label in labels else 0)

    def load_image(self):
        if not (0 <= self.index < len(image_paths)):
            messagebox.showinfo("Done", "All images annotated.")
            return

        self.current_path = image_paths[self.index]
        rel_path = os.path.relpath(self.current_path, image_root_folder)

        image = Image.open(self.current_path).convert("RGBA")
        image.thumbnail((512, 512))
        self.tk_image = ImageTk.PhotoImage(image)

        self.label_image.config(image=self.tk_image)
        self.label_image.image = self.tk_image

        # Load existing annotation if exists
        if rel_path in annotations:
            self.fill_selection(annotations[rel_path])
        else:
            self.clear_selection()

    def save_and_next(self):
        selected = [label for label, var in self.affordance_vars if var.get() == 1]
        rel_path = os.path.relpath(self.current_path, image_root_folder)

        annotations[rel_path] = selected

        with open(output_json_path, "w") as f:
            json.dump(annotations, f, indent=2)

        self.index += 1
        self.load_image()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.load_image()

root = tk.Tk()
tool = AffordanceAnnotator(root)
root.mainloop()
