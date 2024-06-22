import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json
from pathlib import Path

Folder_path = "Data/GameTile/old_dataset/001-test/"
out_path = "Data/GameTile/Json/"
out_file = out_path+ "labeled_directions.json"



# Initialize global variables
image_directory = Folder_path
image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
current_index = 0
labels = {}
current_labels = []
current_image = ""

# Create output directory if it doesn't exist
output_file = out_file


def getImageName(image_path):
    # image_name = os.path.basename(image_path)
    image_name = Path(image_path).stem
    # print(image_name)
    return image_name

# Function to save the label
def label_image(direction):
    current_labels.append(direction)
    log_label.config(text="\n".join(current_labels))

# Function to save labels to JSON
def save_labels():
    with open(output_file, 'w') as f:
        json.dump(labels, f, indent=4)
    print("Labels saved!")
    label.config(text="All labels saved.")
    log_label.config(text="")

def next_image():
    global current_index, current_labels, current_image
    print("current image = ", current_image)
    print(image_files)
    if current_image != "" and current_image not in labels:
        labels[current_image] = current_labels
        print(current_image, current_index, current_labels)
        current_labels = []
        current_index += 1

    if current_index < len(image_files):
        img_path = os.path.join(image_directory, image_files[current_index])

        current_image = getImageName(img_path)
        # labels[getImageName(img_path)] = current_labels

        if current_index < len(image_files):
            load_image(img_path)
        else:
            label.config(text="No more images to label.")
            canvas.delete("all")
            log_label.config(text="")
    else:
        if current_image != "" and current_image not in labels:
            labels[current_image] = current_labels
            print(current_image, current_index, current_labels)
        save_labels()        

# Function to load an image
def load_image(img_path):
    img = Image.open(img_path)
    img = img.resize((500, 500), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk
    label.config(text=os.path.basename(img_path))
    log_label.config(text="")

# Initialize the main window
root = tk.Tk()
root.title("Image Labeling Tool")

# Create a canvas to display the image
canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

# Create a label to show the image file name
label = tk.Label(root, text="")
label.pack()

# Create a log label to show clicked buttons
log_label = tk.Label(root, text="", justify=tk.LEFT, anchor="w")
log_label.pack()

# Create direction buttons
buttons_frame = tk.Frame(root)
buttons_frame.pack()

directions = ["left-top",  "left-down", "top-left", "top-right", "right-top", "right-down", "down-left",  "down-right"]
for direction in directions:
    btn = tk.Button(buttons_frame, text=direction, command=lambda d=direction: label_image(d))
    btn.pack(side=tk.LEFT)

# Create a 'Next' button to go to the next image
next_btn = tk.Button(root, text="Next", command=next_image)
next_btn.pack()

# # Load the first image
# if image_files:
#     img_path = os.path.join(image_directory, image_files[current_index])
#     load_image(img_path)
#     current_image = getImageName(img_path)
#     print(current_image)
# else:
#     label.config(text="No images found in the directory.")

# Run the Tkinter main loop
root.mainloop()