import os, json, tkinter as tk
from PIL import Image, ImageTk

# === CONFIGURATION ===
TILE_ROOT = "Data/GameTile/small_dataset/Tiles"
TILE_LIST_FILE = "Data/GameTile/connectivity_sampled_tiles.json"
OUTPUT_JSON = "Data/GameTile/labeled_connectivity_manual.json"

DIRECTIONS = ["top_left", "top_right", "left_top", "left_down", "down_left", "down_right", "right_top", "right_down"]

class ConnectivityLabeler:
    def __init__(self, root, tile_root, tile_list, output_file):
        self.root = root
        self.tile_root = tile_root
        self.tiles = tile_list
        self.output_file = output_file
        self.index = 0
        self.labels = {}

        self.canvas = tk.Label(root)
        self.canvas.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.vars = {}
        self.buttons = {}
        for d in DIRECTIONS:
            self.vars[d] = tk.IntVar()
            self.buttons[d] = tk.Checkbutton(self.button_frame, text=d, variable=self.vars[d])
            self.buttons[d].pack(side='left')

        self.info = tk.Label(root, text="")
        self.info.pack()

        nav = tk.Frame(root)
        nav.pack()
        tk.Button(nav, text="Save", command=self.save_label).pack(side='left')
        tk.Button(nav, text="Next", command=self.next_image).pack(side='left')
        tk.Button(nav, text="Back", command=self.prev_image).pack(side='left')

        self.load_image()

    def load_image(self):
        rel_path = self.tiles[self.index]
        full_path = os.path.join(self.tile_root, rel_path)
        self.tk_img = ImageTk.PhotoImage(Image.open(full_path).resize((128,128)))
        self.canvas.config(image=self.tk_img)
        self.info.config(text=f"{rel_path} ({self.index+1}/{len(self.tiles)})")

        # Reset checkboxes
        for d in DIRECTIONS:
            self.vars[d].set(0)

        # Load previous labels if available
        if rel_path in self.labels:
            for d in self.labels[rel_path]:
                if d in self.vars: self.vars[d].set(1)

    def save_label(self):
        rel_path = self.tiles[self.index]
        self.labels[rel_path] = [d for d in DIRECTIONS if self.vars[d].get()]
        with open(self.output_file, 'w') as f:
            json.dump(self.labels, f, indent=4)

    def next_image(self): self.save_label(); self.index = min(self.index+1, len(self.tiles)-1); self.load_image()
    def prev_image(self): self.save_label(); self.index = max(self.index-1, 0); self.load_image()

if __name__ == "__main__":
    with open(TILE_LIST_FILE) as f:
        tile_list = json.load(f)

    root = tk.Tk()
    root.title("Connectivity Labeler (Manual)")
    app = ConnectivityLabeler(root, TILE_ROOT, tile_list, OUTPUT_JSON)
    root.mainloop()
