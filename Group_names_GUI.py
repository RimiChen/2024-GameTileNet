import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# === CONFIG ===
INPUT_JSON = "Data/GameTile/complete_author_json/cleaned_labels.json"
IMAGE_ROOT = "Data/GameTile/complete_author_cleaned"
OUTPUT_JSON = "Data/GameTile/complete_author_json/manual_group_labels.json"
RESIZE_TO = (128, 128)  # Image display size

# === LOAD DATA ===
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        saved_labels = json.load(f)
else:
    saved_labels = {}

# === TKINTER UI ===
class LabelingApp:
    def __init__(self, master, data):
        self.master = master
        self.master.title("Manual Group Labeling")
        self.data = data
        self.index = 0
        self.label_vars = []
        self.image_label = None
        self.canvas = None
        self.group_box = None
        self.info_label = None
        self.image_panel = None

        self.setup_ui()
        self.load_image()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack()

        self.image_panel = tk.Label(self.master)
        self.image_panel.pack()

        self.group_box = ttk.LabelFrame(self.master, text="Select Group Token(s)")
        self.group_box.pack(padx=10, pady=5)

        self.info_label = tk.Label(self.master, text="")
        self.info_label.pack()

        btn_frame = tk.Frame(self.master)
        btn_frame.pack()

        tk.Button(btn_frame, text="Save & Next", command=self.save_and_next).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Skip", command=self.next_image).pack(side=tk.LEFT, padx=5)

    def load_image(self):
        if self.index >= len(self.data):
            self.info_label.config(text="All images labeled!")
            self.master.quit()
            return

        entry = self.data[self.index]
        full_path = os.path.join(IMAGE_ROOT, entry["relative_path"].replace("\\", "/"))

        if not os.path.exists(full_path):
            self.index += 1
            self.load_image()
            return

        try:
            img = Image.open(full_path).convert("RGBA")
            img.thumbnail(RESIZE_TO)
            photo = ImageTk.PhotoImage(img)
            self.image_panel.config(image=photo)
            self.image_panel.image = photo
        except Exception as e:
            print("Image failed to load:", full_path)
            self.index += 1
            self.load_image()
            return

        # Update label
        name = entry["cleaned_label"]
        self.info_label.config(text=f"[{self.index+1}/{len(self.data)}] {name}")
        self.build_checkboxes(name)

    def build_checkboxes(self, label_name):
        for widget in self.group_box.winfo_children():
            widget.destroy()
        self.label_vars.clear()

        tokens = label_name.lower().replace("-", "_").split("_")
        for tok in tokens:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.group_box, text=tok, variable=var)
            cb.pack(side=tk.LEFT, padx=2)
            self.label_vars.append((tok, var))

    def save_and_next(self):
        selected = [tok for tok, var in self.label_vars if var.get()]
        if selected:
            entry = self.data[self.index]
            image_path = os.path.join(IMAGE_ROOT, entry["relative_path"].replace("\\", "/"))
            saved_labels[image_path] = {
                "detailed_name": entry["cleaned_label"],
                "selected_group_tokens": selected
            }
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(saved_labels, f, indent=2)

        self.index += 1
        self.load_image()

    def next_image(self):
        self.index += 1
        self.load_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root, data)
    root.mainloop()
