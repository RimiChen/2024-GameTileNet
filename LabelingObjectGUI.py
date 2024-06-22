import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os


json_path = "Data/GameTile/Json/"
# image_folder = json_path + "001-test/"
image_list_path = json_path + "objects_001-test.json"
out_path = "Data/GameTile/Json/"
out_file = out_path+"label_objects.json"


# Load image list from JSON file
def load_image_list(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

# Initialize global variables
image_list = []
current_index = 0
results = []

# Function to handle user input
def record_answer():
    global current_index
    object_name = entry.get()
    is_complete = not_incomplete_var.get() == 0
    results.append({
        "image": image_list[current_index],
        "object_name": object_name,
        "is_complete_object": is_complete
    })
    entry.delete(0, tk.END)
    not_incomplete_var.set(0)
    current_index += 1
    if current_index < len(image_list):
        display_image(image_list[current_index])
    else:
        save_results()
        label.config(text="All images have been labeled.")
        canvas.delete("all")

# Save results to JSON
def save_results():
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=4)
    print(out_file)

# Display the current image
def display_image(image_path):
    image = Image.open(image_path)
    image = image.resize((250, 250), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk
    label.config(text=os.path.basename(image_path))

# Initialize the main window
root = tk.Tk()
root.title("Image Labeling Tool")

# Create a canvas to display the images
canvas = tk.Canvas(root, width=250, height=250)
canvas.pack()

# Create a label to show the image file name
label = tk.Label(root, text="")
label.pack()

# Create an entry widget for typing object names
entry = tk.Entry(root, width=50)
entry.pack()

# Create a variable and checkbox for indicating incomplete objects
not_incomplete_var = tk.IntVar()
not_incomplete_checkbox = tk.Checkbutton(root, text="Not a complete object", variable=not_incomplete_var)
not_incomplete_checkbox.pack()

# Create a button for recording the answer and moving to the next image
submit_btn = tk.Button(root, text="Submit", command=record_answer)
submit_btn.pack()

# Load the first image
image_list = load_image_list(image_list_path)
if image_list:
    display_image(image_list[current_index])
else:
    label.config(text="No images found in the JSON file.")

# Run the Tkinter main loop
root.mainloop()