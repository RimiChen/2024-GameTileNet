from PIL import Image
import numpy as np
import math
from pathlib import Path
import matplotlib.pyplot as plt
import cv2
from mpl_toolkits.axes_grid1 import make_axes_locatable

### dispaly image
def DisplayImage(image_path, tile_size):
    tile_map_image = Image.open(image_path)
    plt.imshow(tile_map_image)    
    image_array = np.array(tile_map_image)
    # print(image_array.shape)
    # plt.imshow(image_array)
    # Customize the x-axis and y-axis labels
    tick_interval = tile_size
    # print(image_array.shape[1])
    ticks_x = np.arange(0, image_array.shape[1], tick_interval)
    ticks_y = np.arange(0, image_array.shape[0], tick_interval)
    labels_x = np.arange(len(ticks_x))
    labels_y = np.arange(len(ticks_y))
    print(labels_x)
    print(labels_y)
 

    plt.xticks(ticks_x, labels_x)
    plt.yticks(ticks_y, labels_y)    
    
    plt.show()  




def draw_grid(image_path, tile_size):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # Check if the image is loaded successfully
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Create a figure with the same size as the image
    dpi = 100  # Dots per inch for the figure
    fig_size = (width / dpi, height / dpi)
    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

    # Display the image
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Draw grid lines based on the tile size
    for x in range(0, width, tile_size):
        ax.axvline(x=x, color='yellow', linewidth=1)
    for y in range(0, height, tile_size):
        ax.axhline(y=y, color='yellow', linewidth=1)

    # Set the major ticks based on the tile size
    major_ticks_x = np.arange(0, width, tile_size)
    major_ticks_y = np.arange(0, height, tile_size)

    # Set the tick labels to show the coordinates
    ax.set_xticks(major_ticks_x)
    ax.set_yticks(major_ticks_y)
    ax.set_xticklabels(major_ticks_x)
    ax.set_yticklabels(major_ticks_y)

    # Set the axis labels
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # Ensure the aspect ratio is equal to prevent squeezing
    ax.set_aspect('equal')

    # Disable axis
    ax.axis('off')

    # Disable the toolbar for zoom/pan
    plt.rcParams['toolbar'] = 'None'

    # Set tight layout to make sure the figure doesn't resize
    plt.tight_layout()

    # Show the plot without resizing the image
    plt.show()