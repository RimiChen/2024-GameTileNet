# image_path = 'Data/GameTile/001-Grassland01.png'
from PIL import Image
import numpy as np
import math
from pathlib import Path
from rembg import remove
from io import BytesIO

import matplotlib.pyplot as plt
# from matplotlib.pyplot import imshow
import os
import json
from skimage.metrics import structural_similarity as ssim
from CheckTileSimilarity import *
from DisplayImage import *


TILE_SIZE = 32
TILE_WIDTH = 32
TITLE_HEIGHT = 64
SIMILARITY_THRESHOLDS = 0.5 

# tileset_path = "Data/GameTile/Tilesets/"
tileset_path = "Data/GameTile/small_Tilesets/"

out_path = "Data/GameTile/small_dataset/"
black_back_image = "Data/GameTile/black.png"
white_back_image = "Data/GameTile/white.png"
blank_back_image = "Data/GameTile/blank.png"
# black_path = out_path

### get image name from image path
def getImageName(image_path):
    # image_name = os.path.basename(image_path)
    image_name = Path(image_path).stem
    # print(image_name)
    return image_name

### slice tile with assigned edge size
def SliceTileRectangle(image_path, out_path, tile_size, starting_index):
    # Load the tile map image
    tile_map_image = Image.open(image_path)
    plt.imshow(tile_map_image)
    plt.show()
    width, height = tile_map_image.size
    # print(width)
    # print(height)


    # Define the item sizes in the tile map (x, y, width, height)
    # tile_size = TILE_SIZE
    # (x1, y1, x2, y2)
    w_shift = 0
    h_shift = 0
    items = []
    while h_shift < height:
        while w_shift < width:
            x1 = w_shift
            y1 = h_shift
            items.append((x1, y1,  tile_size,  tile_size))
            print((x1, y1,  tile_size,  tile_size))

            w_shift = w_shift +  tile_size
        
        w_shift = 0
        h_shift = h_shift + tile_size

    print("End record bounding boxes!")

    # Iterate through the defined items and extract each one
    tiles = []
    for (x, y, width, height) in items:
        tile = tile_map_image.crop((x, y, x + width, y + height))
        tiles.append(tile)

    # Save or use the extracted tiles
    directory = out_path + str(tile_size)+"x"+str(tile_size) 
    if not os.path.exists(directory):
        os.makedirs(directory)

    for index, tile in enumerate(tiles):
        # new_image_path = 'Data/GameTile/dataset/tile_{index}.png'
        tile.save(directory+"/tiles_"+str(starting_index + index)+".png")

    return index

### slice tile with assigned width and height
def SliceTile(image_path, out_path, tile_width, tile_height, starting_index):
    # Load the tile map image
    tile_map_image = Image.open(image_path)
    plt.imshow(tile_map_image)
    plt.show()
    width, height = tile_map_image.size
    # print(width)
    # print(height)


    w_shift = 0
    h_shift = 0
    items = []
    while h_shift < height:
        while w_shift < width:
            x1 = w_shift
            y1 = h_shift
            items.append((x1, y1,  tile_width,  tile_height))
            print((x1, y1,  tile_width,  tile_height))

            w_shift = w_shift +  tile_width
        
        w_shift = 0
        h_shift = h_shift + tile_height

    print("End record bounding boxes!")




    # Iterate through the defined items and extract each one
    tiles = []
    for (x, y, width, height) in items:
        tile = tile_map_image.crop((x, y, x + width, y + height))
        tiles.append(tile)

    # Save or use the extracted tiles
    directory = out_path + str(tile_width)+"x"+str(tile_height) 
    if not os.path.exists(directory):
        os.makedirs(directory)

    for index, tile in enumerate(tiles):
        # new_image_path = 'Data/GameTile/dataset/tile_{index}.png'
        tile.save(directory+"/tiles_"+str(starting_index + index)+".png")

    return index

  

### target: slice tiles with certain size, but label the file with x, y coordinate
def SliceTileCoordinate(image_path, out_path, tile_size):
    # Load the tile map image
    tile_map_image = Image.open(image_path)
    # plt.imshow(tile_map_image)    
    # image_array = np.array(tile_map_image)
    # # print(image_array.shape)
    # # plt.imshow(image_array)
    # # Customize the x-axis and y-axis labels
    # tick_interval = 32
    # # print(image_array.shape[1])
    # ticks_x = np.arange(0, image_array.shape[1], tick_interval)
    # ticks_y = np.arange(0, image_array.shape[0], tick_interval)
    # labels_x = np.arange(len(ticks_x))
    # labels_y = np.arange(len(ticks_y))
    # print(labels_x)
    # print(labels_y)
 

    # plt.xticks(ticks_x, labels_x)
    # plt.yticks(ticks_y, labels_y)    
    

    # plt.show()

    width, height = tile_map_image.size
    # print(width)
    # print(height)


    # Define the item sizes in the tile map (x, y, width, height)
    # tile_size = TILE_SIZE
    # (x1, y1, x2, y2)
    w_shift = 0
    h_shift = 0
    
    items = []
    while h_shift < height:
        while w_shift < width:
            x1 = w_shift
            y1 = h_shift
            items.append((x1, y1,  tile_size,  tile_size))
            # print((x1, y1,  tile_size,  tile_size))

            w_shift = w_shift +  tile_size
        
        w_shift = 0
        h_shift = h_shift + tile_size

    print("End record bounding boxes!  ", image_path)

    # Iterate through the defined items and extract each one
    tiles = {}
    tile_annotations = {}
    for (x, y, width, height) in items:
        x_index = math.floor(x/tile_size)
        y_index = math.floor(y/tile_size)
        tile_key = str(x_index) +"_"+ str(y_index)
        tile = tile_map_image.crop((x, y, x + width, y + height))
        # tiles[tile_key] = {}
        tiles[tile_key] = tile
        #tile_name	is_part	is_whole source	belong_to is_texture is_object	connection	object_class
        tile_annotations[tile_key] = {}
        tile_annotations[tile_key]["source"] = getImageName(image_path)
        # tile_annotations[tile_key]["tile"] = tile
        tile_annotations[tile_key]["x_index"] = x_index
        tile_annotations[tile_key]["y_index"] = y_index
        tile_annotations[tile_key]["name"] = "tiles_"+tile_key

    # Save or use the extracted tiles
    directory = out_path + "/"+getImageName(image_path)
    no_reduce_directory = out_path + "/"+getImageName(image_path)+"_full"
    black_directory = out_path + "/"+getImageName(image_path)+"_black"
    white_directory = out_path + "/"+getImageName(image_path)+"_white"
    # print("Path:", directory, black_directory, white_directory)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(no_reduce_directory):
        os.makedirs(no_reduce_directory)        
    if not os.path.exists(black_directory):
        os.makedirs(black_directory)

    if not os.path.exists(white_directory):
        os.makedirs(white_directory)

    for key in tile_annotations.keys():
        new_path = directory+"/"+ tile_annotations[key]["name"]+".png"
        new_no_reduce_path = no_reduce_directory+"/"+ tile_annotations[key]["name"]+".png"
        new_black_path = black_directory+"/"+ tile_annotations[key]["name"]+".png"
        new_white_path = white_directory+"/"+ tile_annotations[key]["name"]+".png"

        tiles[key].save(new_path)
        tiles[key].save(new_no_reduce_path)

        # if is_image_mostly_blank(new_path):
        if is_almost_transparent(new_path):
        
            # if an blank image
            os.remove(new_path)
            # if not os.path.exists(new_path):
            #     print(" Succeful remove: ", new_path)
        else:
            # not blank
            overlay_images(black_back_image, new_path, new_black_path)
            overlay_images(white_back_image, new_path, new_white_path)






    # for index, tile in enumerate(tiles):
    #     # new_image_path = 'Data/GameTile/dataset/tile_{index}.png'
    #     tile.save(directory+"/tiles_"+str(starting_index + index)+".png")

    return tile_annotations

# get image index from image path
def get_image_index(image_path):
    image_name = Path(image_path).stem
    name_array = image_name.split("_")
    last_two = name_array[-2:]
    image_x_index = last_two[0]
    image_y_index = last_two[1]
    print("x, y = ", image_x_index, image_y_index)

    return image_x_index, image_y_index

## load all tileset
def get_file_list(folder_path):
    """
    Get a list of files in the specified folder, excluding subfolders.

    Parameters:
    folder_path (str): Path to the folder to scan for files.

    Returns:
    list: List of file paths.
    """
    file_list = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            file_list.append(entry.path)
    return file_list

## remove backgroud if the tileset has background
def remove_background(image_path):
    """
    Remove the background from an image using rembg library.

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    Image object with background removed.
    """
    with open(image_path, 'rb') as image_file:
        input_image = image_file.read()
    
    output_image = remove(input_image)
    img = Image.open(BytesIO(output_image))
    return img

def convert_to_png_remove_back(folder_path):
    """
    Convert images in a folder to PNG format and remove background for non-PNG images.

    Parameters:
    folder_path (str): Path to the folder containing images.
    """
    file_list = [entry.path for entry in os.scandir(folder_path) if entry.is_file()]

    for file_path in file_list:
        file_name, file_ext = os.path.splitext(file_path)
        
        # Skip if already a PNG
        if file_ext.lower() == '.png':
            continue
        
        # Remove background for non-PNG images
        print("current file is ", file_ext)
        image = remove_background(file_path)
        
        if image:
            png_path = f"{file_name}.png"
            image.save(png_path, "PNG")
            print(f"Converted and saved: {png_path}")
        else:
            print(f"Failed to process: {file_path}")

def convert_to_png_only(folder_path):
    """
    Convert all images in the specified folder to PNG format.

    Parameters:
    folder_path (str): Path to the folder containing images.
    """
    file_list = [entry.path for entry in os.scandir(folder_path) if entry.is_file()]

    for file_path in file_list:
        file_name, file_ext = os.path.splitext(file_path)
        
        # Skip if already a PNG
        if file_ext.lower() == '.png':
            continue
        
        try:
            image = Image.open(file_path)
            png_path = f"{file_name}.png"
            image.save(png_path, "PNG")
            print(f"Converted and saved: {png_path}")
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

# overlap images
def overlay_images(background_path, foreground_path, output_path):
    """
    Overlay a foreground image on a background image and save the result.

    Parameters:
    background_path (str): Path to the background image file.
    foreground_path (str): Path to the foreground image file.
    output_path (str): Path to save the output image.
    """
    # Open the background and foreground images
    background = Image.open(background_path).convert("RGBA")
    foreground = Image.open(foreground_path).convert("RGBA")

    # Resize the background to match the size of the foreground
    background = background.resize(foreground.size, Image.LANCZOS)

    # Composite the images
    combined = Image.alpha_composite(background, foreground)

    # Save the result
    combined.save(output_path)
    # print(f"Image saved to {output_path}")

if __name__ == "__main__":

    print("This script slice the tile sets")

    # image_paths = [
    #     "Data/GameTile/001-Grassland01.png",
    #     # "Data/GameTile/010-CastleTown02.png",
    #     # "Data/GameTile/008-Snowfield01.png",
    #     # "Data/GameTile/005-Beach01.png",
    #     # "Data/GameTile/006-Desert01.png",
    #     # "Data/GameTile/009-CastleTown01.png",
    #     # "Data/GameTile/026-Castle02.png",
    #     # "Data/GameTile/0003-base_out_atlas.png",
    #     # "Data/GameTile/0003-terrain_atlas.png",
    #     # "Data/GameTile/0005-obj_misk_atlas.png",
    # ]



    folder_path = tileset_path  # Replace with your folder path
    convert_to_png_only(folder_path)


    folder_path = tileset_path  # Replace with your folder path
    files = get_file_list(folder_path)
    print(f"Files in '{folder_path}':")
    file_list = []
    for file in files:
        if file not in file_list:
            file_list.append(file)
            # print(file)

    print(json.dumps(file_list, indent=4))





    index = 0
    for image_path in file_list:
        image_source_name = getImageName(image_path)
        # DisplayImage(image_path, TILE_SIZE)
        tileset_annotations = SliceTileCoordinate(image_path, out_path, TILE_SIZE)
        with open(out_path+image_source_name+"_step_"+str(index)+".json", "w") as f:
            json.dump(tileset_annotations, f)

    #     # Find adjacent

    #     # starting_index = SliceTile(image_path, out_path, tile_width, tile_height, starting_index)
    # adjacent_test_pairs = []
    # index = 0
    # folder_path = "010-CastleTown02"
    # # choose testing pairs randomly
    # pair = {}
    # pair["image_1"] = folder_path+"/tiles_2_0.png"
    # pair["image_2"] = folder_path+"/tiles_2_1.png"
    # adjacent_test_pairs.append(pair)



    # image_path_1 = out_path+folder_path+"/tiles_2_0.png"
    # image_path_2 = out_path+folder_path+"/tiles_2_1.png"
    # isAdjacent = CheckAdjacent(image_path_1, image_path_2)
    # print("isAdjacent = ", isAdjacent)

    ### find segment and clear empty


 
    # folder_path = "010-CastleTown02"
    # image_path_1 = "Data/GameTile/dataset/"+folder_path+"/tiles_0_0.png"
    # image_path_2 = "Data/GameTile/dataset/"+folder_path+"/tiles_1_0.png"
    # isAdjacent = CheckAdjacent(image_path_1, image_path_2)
    # print("isAdjacent = ", isAdjacent)
