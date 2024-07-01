import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

from CheckTileSimilarity import *

index = 19
json_path = "Data/GameTile/small_SimilarityLabel_pairs_verify/"
image_pair_file = json_path + "output_image_pairs_"+str(index)+".json"
print("source: ", image_pair_file)
out_path = "Data/GameTile/small_SimilarityLabel_verify/"
out_file = out_path+"label_similarity_"+str(index)+".json"
print("result: ", out_file)

# Load pairs of images from JSON file
def load_image_pairs(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

# Determine the arrangement of images based on their filenames
def arrange_images(image1, image2):
    base1, ext1 = os.path.splitext(os.path.basename(image1))
    base2, ext2 = os.path.splitext(os.path.basename(image2))
    
    x1, y1 = map(int, base1.split('_')[1:])
    x2, y2 = map(int, base2.split('_')[1:])
    
    if x1 == x2 and y1 == y2 - 1:
        return "vertical", image2, image1
    elif x1 == x2 and y1 == y2 + 1:
        return "vertical", image1, image2
    elif x1 == x2 - 1 and y1 == y2:
        return "horizontal", image1, image2
    elif x1 == x2 + 1 and y1 == y2:
        return "horizontal", image2, image1
    else:
        return "unknown", image1, image2

# Initialize global variables
image_pairs = []
current_index = 0
results = []

# Function to handle user input
def record_answer(connected):
    global current_index
    similarity = checkSimilarity(image_pairs[current_index]['image1'], image_pairs[current_index]['image2'])
    print(image_pairs[current_index]['image1'], image_pairs[current_index]['image2'], " similarity = ", similarity)

    results.append({
        "image1": image_pairs[current_index]['image1'],
        "image2": image_pairs[current_index]['image2'],
        "connected": connected,
        "similarity": similarity
    })
    current_index += 1
    if current_index < len(image_pairs):
        display_images(image_pairs[current_index])
    else:
        save_results()
        label.config(text="All image pairs have been reviewed.")
        canvas1.delete("all")
        canvas2.delete("all")

# Save results to JSON
def save_results():
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=4)
    print("Results saved to results.json")

# Display the current pair of images
def display_images(pair):
    orientation, img1, img2 = arrange_images(pair['image1'], pair['image2'])
    
    image1 = Image.open(img1)
    image2 = Image.open(img2)
    
    image1 = image1.resize((250, 250), Image.LANCZOS)
    image2 = image2.resize((250, 250), Image.LANCZOS)
    
    img1_tk = ImageTk.PhotoImage(image1)
    img2_tk = ImageTk.PhotoImage(image2)
    
    canvas1.create_image(0, 0, anchor=tk.NW, image=img1_tk)
    canvas1.image = img1_tk
    
    canvas2.create_image(0, 0, anchor=tk.NW, image=img2_tk)
    canvas2.image = img2_tk
    
    if orientation == "horizontal":
        canvas1.pack(side=tk.LEFT)
        canvas2.pack(side=tk.RIGHT)
    else:  # vertical
        canvas1.pack(side=tk.BOTTOM)
        canvas2.pack(side=tk.TOP)
    
    label.config(text=f"Reviewing pair {current_index + 1} of {len(image_pairs)}")

# Initialize the main window
root = tk.Tk()
root.title("Image Pair Connection Review Tool")

# Create a canvas to display the images
canvas1 = tk.Canvas(root, width=250, height=250)
canvas2 = tk.Canvas(root, width=250, height=250)

# Create a label to show the progress
label = tk.Label(root, text="")
label.pack()

# Create buttons for user input
buttons_frame = tk.Frame(root)
buttons_frame.pack()

connected_btn = tk.Button(buttons_frame, text="Connected", command=lambda: record_answer(True))
connected_btn.pack(side=tk.LEFT)

not_connected_btn = tk.Button(buttons_frame, text="Not Connected", command=lambda: record_answer(False))
not_connected_btn.pack(side=tk.RIGHT)

# Load the first pair of images
image_pairs = load_image_pairs(image_pair_file)
if image_pairs:
    display_images(image_pairs[current_index])
else:
    label.config(text="No image pairs found in the JSON file.")

# Run the Tkinter main loop
root.mainloop()