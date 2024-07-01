import cv2
import numpy as np
import matplotlib.pyplot as plt
import os


tileset_folder = "Data/GameTile/small_Tilesets/"
tileset_name = "001_001.png"
tile_size = 32
out_folder = "Data/GameTile/small_tileset_grids/"

def draw_grid(image_path, tile_size, output_dir):
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
        ax.axvline(x=x, color='red', linewidth=1)
    for y in range(0, height, tile_size):
        ax.axhline(y=y, color='red', linewidth=1)

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

    # Create output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract tileset name from image path
    tileset_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_dir, f'{tileset_name}_grid.png')

    # Save the plot to the output folder
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

def process_tileset_images(input_folder, output_dir, tile_size):
    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            image_path = os.path.join(input_folder, filename)
            draw_grid(image_path, tile_size, output_dir)

#### saved in separeate folders            
# def draw_grid(image_path, tile_size, output_dir):
#     # Load the image
#     image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
#     # Check if the image is loaded successfully
#     if image is None:
#         print(f"Error: Unable to load image at {image_path}")
#         return

#     # Get the dimensions of the image
#     height, width = image.shape[:2]

#     # Create a figure with the same size as the image
#     dpi = 100  # Dots per inch for the figure
#     fig_size = (width / dpi, height / dpi)
#     fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

#     # Display the image
#     ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

#     # Draw grid lines based on the tile size
#     for x in range(0, width, tile_size):
#         ax.axvline(x=x, color='red', linewidth=1)
#     for y in range(0, height, tile_size):
#         ax.axhline(y=y, color='red', linewidth=1)

#     # Set the major ticks based on the tile size
#     major_ticks_x = np.arange(0, width, tile_size)
#     major_ticks_y = np.arange(0, height, tile_size)

#     # Set the tick labels to show the coordinates
#     ax.set_xticks(major_ticks_x)
#     ax.set_yticks(major_ticks_y)
#     ax.set_xticklabels(major_ticks_x)
#     ax.set_yticklabels(major_ticks_y)

#     # Set the axis labels
#     ax.set_xlabel('X-axis')
#     ax.set_ylabel('Y-axis')

#     # Ensure the aspect ratio is equal to prevent squeezing
#     ax.set_aspect('equal')

#     # Disable axis
#     ax.axis('off')

#     # Disable the toolbar for zoom/pan
#     plt.rcParams['toolbar'] = 'None'

#     # Set tight layout to make sure the figure doesn't resize
#     plt.tight_layout()

#     # Create output folder if it doesn't exist
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # Extract tileset name from image path
#     tileset_name = os.path.splitext(os.path.basename(image_path))[0]
#     output_path = os.path.join(output_dir, f'{tileset_name}_grid.png')

#     # Save the plot to the output folder
#     plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
#     plt.close(fig)

# def process_tileset_images(input_folder, output_base_dir, tile_size):
#     # Process each image in the input folder
#     for filename in os.listdir(input_folder):
#         if filename.endswith('.png'):
#             image_path = os.path.join(input_folder, filename)
#             output_dir = os.path.join(output_base_dir, os.path.splitext(filename)[0])
#             draw_grid(image_path, tile_size, output_dir)

# Example usage
input_folder = tileset_folder  # Replace with your input folder path containing tileset images
output_base_dir = out_folder  # Base directory to save the grid images
tile_size = 32  # Replace with your desired tile size (e.g., 32 or 16)
process_tileset_images(input_folder, output_base_dir, tile_size)