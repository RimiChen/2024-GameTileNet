import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json

Folder_path = "Data/GameTile/old_dataset/001-test/"
out_path = "Data/GameTile/Json/"
out_file = out_path+ "labeled_directions.json"

image_directory = Folder_path
image_files = [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
current_index = 0
labels = {}
current_labels = []
current_image = ""


# Function to handle button click and record connectivity
def button_click(position):
    if position not in connectivity_list:
        connectivity_list.append(position)
    update_connectivity_label()

# Function to update the connectivity label with the recorded positions
def update_connectivity_label():
    connectivity_label.config(text="Connectivity: " + str(connectivity_list))

# Function to split the image into four sub-images and resize them
def split_image(image_path):
    img = Image.open(image_path)
    width, height = img.size
    
    # Resize image to make it fit better in the grid
    img = img.resize((300, 300), Image.LANCZOS)
    
    # Calculate half width and height for splitting
    half_width, half_height = img.size[0] // 2, img.size[1] // 2

    # Crop the image into 4 parts
    top_left = img.crop((0, 0, half_width, half_height))
    top_right = img.crop((half_width, 0, img.size[0], half_height))
    bottom_left = img.crop((0, half_height, half_width, img.size[1]))
    bottom_right = img.crop((half_width, half_height, img.size[0], img.size[1]))
    
    return top_left, top_right, bottom_left, bottom_right

# Function to load the next image and update the display
def next_image():
    global current_image_index, connectivity_list, connectivity_data

    # Store current image's connectivity before moving to the next one
    if current_image_index > 0:
        image_key = os.path.splitext(os.path.basename(image_files[current_image_index - 1]))[0]  # Use the image file name as key
        connectivity_data[image_key] = connectivity_list

    # Clear the current connectivity list for the new image
    connectivity_list = []
    update_connectivity_label()

    # Check if there are more images in the folder
    if current_image_index < len(image_files):
        # Load and display the next image
        image_path = image_files[current_image_index]
        top_left, top_right, bottom_left, bottom_right = split_image(image_path)

        # Convert sub-images into Tkinter-compatible format
        tk_top_left = ImageTk.PhotoImage(top_left)
        tk_top_right = ImageTk.PhotoImage(top_right)
        tk_bottom_left = ImageTk.PhotoImage(bottom_left)
        tk_bottom_right = ImageTk.PhotoImage(bottom_right)

        # Set the new images on the labels
        labels[0].config(image=tk_top_left)
        labels[0].image = tk_top_left
        labels[1].config(image=tk_top_right)
        labels[1].image = tk_top_right
        labels[2].config(image=tk_bottom_left)
        labels[2].image = tk_bottom_left
        labels[3].config(image=tk_bottom_right)
        labels[3].image = tk_bottom_right

        # Increment the image index
        current_image_index += 1
    else:
        # If no more images, export the connectivity data to JSON
        export_connectivity()

# Function to export the connectivity data to a JSON file
def export_connectivity():
    with open(out_file, "w") as json_file:
        json.dump(connectivity_data, json_file, indent=4)
    print("Connectivity data exported to connectivity_data.json")

# Create the main window
root = tk.Tk()
root.title("4x4 Grid with Image and Buttons")

# Create the connectivity list to track button clicks
connectivity_list = []

# Dictionary to hold connectivity data for each image
connectivity_data = {}

# Create a label to display the connectivity records
connectivity_label = tk.Label(root, text="Connectivity: []", anchor="w")
connectivity_label.grid(row=4, column=0, columnspan=4)

# Get a list of image files from the folder
image_folder = image_directory  # Replace with the path to your image folder
image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
current_image_index = 0

# Create placeholders for the image labels
labels = []

# Create a 4x4 grid with buttons around the image positions
for row in range(4):
    for col in range(4):
        if (row, col) == (1, 1):
            # Create label for top-left sub-image
            label = tk.Label(root, bg="lightgray", width=150, height=150)
            label.grid(row=row, column=col, padx=5, pady=5)
            labels.append(label)
        elif (row, col) == (1, 2):
            # Create label for top-right sub-image
            label = tk.Label(root, bg="lightgray", width=150, height=150)
            label.grid(row=row, column=col, padx=5, pady=5)
            labels.append(label)
        elif (row, col) == (2, 1):
            # Create label for bottom-left sub-image
            label = tk.Label(root, bg="lightgray", width=150, height=150)
            label.grid(row=row, column=col, padx=5, pady=5)
            labels.append(label)
        elif (row, col) == (2, 2):
            # Create label for bottom-right sub-image
            label = tk.Label(root, bg="lightgray", width=150, height=150)
            label.grid(row=row, column=col, padx=5, pady=5)
            labels.append(label)
        elif (row, col) in [(0, 1), (0, 2), (1, 0), (2, 0), (3, 1), (3, 2), (1, 3), (2, 3)]:
            # Place buttons around the image
            button = tk.Button(root, text=f"Button ({row},{col})", command=lambda pos=(row, col): button_click(pos))
            button.grid(row=row, column=col, padx=5, pady=5)

# Create a "Next Image" button
next_button = tk.Button(root, text="Next Image", command=next_image)
next_button.grid(row=5, column=0, columnspan=4, pady=10)

# Load the first image when the window starts
next_image()

# Start the Tkinter event loop
root.mainloop()

# Optional: Export the final image connectivity when the app closes
if current_image_index > 0:
    export_connectivity()