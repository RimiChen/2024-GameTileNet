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


TILE_SIZE = 32
TILE_WIDTH = 32
TITLE_HEIGHT = 64
SIMILARITY_THRESHOLDS = 0.5 

tileset_path = "Data/GameTile/Tilesets/"
out_path = "Data/GameTile/dataset/"

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

    print("End record bounding boxes!")

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
    if not os.path.exists(directory):
        os.makedirs(directory)

    for key in tile_annotations.keys():
        tiles[key].save(directory+"/"+ tile_annotations[key]["name"]+".png")
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
### Computer histogram similarity
def histogram_similarity(vec1, vec2, bins=256):
    # Calculate histograms for each RGBA channel
    hist1_r, _ = np.histogram(vec1[:, 0], bins=bins, range=(0, 256))
    hist1_g, _ = np.histogram(vec1[:, 1], bins=bins, range=(0, 256))
    hist1_b, _ = np.histogram(vec1[:, 2], bins=bins, range=(0, 256))
    hist1_a, _ = np.histogram(vec1[:, 3], bins=bins, range=(0, 256))
    
    hist2_r, _ = np.histogram(vec2[:, 0], bins=bins, range=(0, 256))
    hist2_g, _ = np.histogram(vec2[:, 1], bins=bins, range=(0, 256))
    hist2_b, _ = np.histogram(vec2[:, 2], bins=bins, range=(0, 256))
    hist2_a, _ = np.histogram(vec2[:, 3], bins=bins, range=(0, 256))

    # Normalize histograms
    hist1_r = hist1_r / np.sum(hist1_r)
    hist1_g = hist1_g / np.sum(hist1_g)
    hist1_b = hist1_b / np.sum(hist1_b)
    hist1_a = hist1_a / np.sum(hist1_a)
    
    hist2_r = hist2_r / np.sum(hist2_r)
    hist2_g = hist2_g / np.sum(hist2_g)
    hist2_b = hist2_b / np.sum(hist2_b)
    hist2_a = hist2_a / np.sum(hist2_a)

    # Calculate histogram intersection (a measure of similarity)
    similarity_r = np.minimum(hist1_r, hist2_r).sum()
    similarity_g = np.minimum(hist1_g, hist2_g).sum()
    similarity_b = np.minimum(hist1_b, hist2_b).sum()
    similarity_a = np.minimum(hist1_a, hist2_a).sum()
    
    # Calculate overall similarity
    overall_similarity = (similarity_r + similarity_g + similarity_b + similarity_a) / 4.0
    
    return overall_similarity
### computer SSIM
def compare_ssim(image1_part, image2_part):
    ssim_index, ssim_map = ssim(image1_part, image2_part, full=True)
    return ssim_index

def oneRowStructureSimilarity(image_1, image_2):
    # Convert images to NumPy arrays
    np_image1 = np.array(image_1)
    np_image2 = np.array(image_2)


    # Extract the first row of image1 and the last row of image2
    top_row_image1 = np_image1[0, :, :]
    bottom_row_image2 = np_image2[-1, :, :]

    # Convert the rows to grayscale
    top_row_image1_gray = np.dot(top_row_image1[...,:3], [0.2989, 0.5870, 0.1140])
    bottom_row_image2_gray = np.dot(bottom_row_image2[...,:3], [0.2989, 0.5870, 0.1140])
    
    # Compute SSIM for the rows
    ssim_rows = compare_ssim(top_row_image1_gray, bottom_row_image2_gray)
    print("SSIM for Rows:", ssim_rows)

    return ssim_rows

def twoRowsStructureSimilarity(image_1, image_2):

    # Convert images to NumPy arrays
    np_image1 = np.array(image_1)
    np_image2 = np.array(image_2)

    # Extract the top two rows of image1 and the bottom two rows of image2
    top_rows_image1 = np_image1[:2, :, :]
    bottom_rows_image2 = np_image2[-2:, :, :]

    # Convert the rows to grayscale
    top_rows_image1_gray = np.dot(top_rows_image1[...,:3], [0.2989, 0.5870, 0.1140])
    bottom_rows_image2_gray = np.dot(bottom_rows_image2[...,:3], [0.2989, 0.5870, 0.1140])
    
    # Compute SSIM for the rows
    ssim_rows = compare_ssim(top_rows_image1_gray, bottom_rows_image2_gray)
    print("SSIM for Rows:", ssim_rows)     

    return ssim_rows

def oneColumnStructureSimilarity(image_1, image_2):
    # Convert images to NumPy arrays
    np_image1 = np.array(image_1)
    np_image2 = np.array(image_2)


    # Extract the first column of image1 and the last column of image2
    left_column_image1 = np_image1[:, 0, :]
    right_column_image2 = np_image2[:, -1, :]

    # Convert the columns to grayscale
    left_column_image1_gray = np.dot(left_column_image1[...,:3], [0.2989, 0.5870, 0.1140])
    right_column_image2_gray = np.dot(right_column_image2[...,:3], [0.2989, 0.5870, 0.1140])
    
    # Compute SSIM for the columns
    ssim_columns = compare_ssim(left_column_image1_gray, right_column_image2_gray)
    print("SSIM for Column:", ssim_columns)

    return ssim_columns

def twoColumnsStructureSimilarity(image_1, image_2):
    # Convert images to NumPy arrays
    np_image1 = np.array(image_1)
    np_image2 = np.array(image_2)


    # Extract the first column of image1 and the last column of image2
    left_columns_image1 = np_image1[:, :2, :]
    right_columns_image2 = np_image2[:, -2:, :]

    # Convert the columns to grayscale
    left_columns_image1_gray = np.dot(left_columns_image1[...,:3], [0.2989, 0.5870, 0.1140])
    right_columns_image2_gray = np.dot(right_columns_image2[...,:3], [0.2989, 0.5870, 0.1140])
    
    # Compute SSIM for the columns
    ssim_columns = compare_ssim(left_columns_image1_gray, right_columns_image2_gray)
    print("SSIM for Columns:", ssim_columns)

    return ssim_columns

# use one row from image 1, and one from image 2 to computer color similarity
def oneLineColorSimilarity(image_1_vec, image_2_vec):
    similarity = histogram_similarity(image_1_vec, image_2_vec, bins=256)
    return similarity
# use two row from image 1, and two from image 2 to compute the average color similarity (0, 1) (30, 31) --> (0, 30)(0, 31)(1, 30) (1, 31) 
def twoLineColorSimilarity(image_1_vec_1, image_1_vec_2, image_2_vec_1, image_2_vec_2) :
    
    similarity_1 = histogram_similarity(image_1_vec_1, image_2_vec_1, bins=256)
    similarity_2 = histogram_similarity(image_1_vec_1, image_2_vec_2, bins=256)
    similarity_3 = histogram_similarity(image_1_vec_2, image_2_vec_1, bins=256)
    similarity_4 = histogram_similarity(image_1_vec_2, image_2_vec_2, bins=256)

    similarity = (similarity_1 + similarity_2 + similarity_3 + similarity_4)/4.0
    
    return similarity



def CheckAdjacent(image_path_1, image_path_2):
    isAdjacent = False
    # connect_directions = []
    image_1 = Image.open(image_path_1).convert('RGBA')
    image_1_w, image_1_h = image_1.size
    image_2 = Image.open(image_path_2).convert('RGBA')
    image_2_w, image_2_h = image_2.size
    plt.imshow(image_1)
    plt.show()    
    plt.imshow(image_2)
    plt.show()    

    if image_1_w != image_2_w or image_1_h != image_2_h:
        print("images should be the same size")
        return isAdjacent

    image_1_x, image_1_y  = get_image_index(image_path_1)
    image_2_x, image_2_y  = get_image_index(image_path_2)
    
    image_1_key = str(image_1_x)+"_"+str(image_1_y)
    image_2_key = str(image_2_x)+"_"+str(image_2_y)

    image_array_1 = {}
    image_array_2 = {}
    ### the four edges: right, left, top, down
    
    # Get the right-most column
    right_edge = image_1_w-1
    image_1_right_most = [image_1.getpixel((right_edge, y)) for y in range(image_1_h)]
    image_array_1["right_1"] = np.array(image_1_right_most)
    image_2_right_most = [image_2.getpixel((right_edge, y)) for y in range(image_2_h)]
    image_array_2["right_1"] = np.array(image_2_right_most)
    right_edge = image_1_w-2
    image_1_right_most = [image_1.getpixel((right_edge, y)) for y in range(image_1_h)]
    image_array_1["right_2"] = np.array(image_1_right_most)
    image_2_right_most = [image_2.getpixel((right_edge, y)) for y in range(image_2_h)]
    image_array_2["right_2"] = np.array(image_2_right_most)

    # Get the left-most column
    left_edge = 0
    image_1_left_most = [image_1.getpixel((left_edge, y)) for y in range(image_1_h)]
    image_array_1["left_1"] = np.array(image_1_left_most)
    image_2_left_most = [image_2.getpixel((left_edge, y)) for y in range(image_2_h)]
    image_array_2["left_1"] = np.array(image_2_left_most)
    left_edge = 1
    image_1_left_most = [image_1.getpixel((left_edge, y)) for y in range(image_1_h)]
    image_array_1["left_2"] = np.array(image_1_left_most)
    image_2_left_most = [image_2.getpixel((left_edge, y)) for y in range(image_2_h)]
    image_array_2["left_2"] = np.array(image_2_left_most)
    # Get the top-most row
    top_edge = 0
    image_1_top_most = [image_1.getpixel((x, top_edge)) for x in range(image_1_w)]
    image_array_1["top_1"] = np.array(image_1_top_most) 
    image_2_top_most = [image_2.getpixel((x, top_edge)) for x in range(image_2_w)]
    image_array_2["top_1"] = np.array(image_2_top_most)
    top_edge = 1
    image_1_top_most = [image_1.getpixel((x, top_edge)) for x in range(image_1_w)]
    image_array_1["top_2"] = np.array(image_1_top_most) 
    image_2_top_most = [image_2.getpixel((x, top_edge)) for x in range(image_2_w)]
    image_array_2["top_2"] = np.array(image_2_top_most)      
    # Get the down-most row   
    down_edge = image_1_h-1
    image_1_down_most = [image_1.getpixel((x, down_edge)) for x in range(image_1_w)]
    image_array_1["down_1"] = np.array(image_1_down_most) 
    image_2_down_most = [image_2.getpixel((x, down_edge)) for x in range(image_2_w)]
    image_array_2["down_1"] = np.array(image_2_down_most) 
    down_edge = image_1_h-2
    image_1_down_most = [image_1.getpixel((x, down_edge)) for x in range(image_1_w)]
    image_array_1["down_2"] = np.array(image_1_down_most) 
    image_2_down_most = [image_2.getpixel((x, down_edge)) for x in range(image_2_w)]
    image_array_2["down_2"] = np.array(image_2_down_most) 


    
    # second image at top x = 0, y = -1, , compare top from image 1, and down from image 2
    if image_1_x == image_2_x and image_1_y > image_2_y:
        print("Check top adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["top_1"], image_array_2["down_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["top_1"], image_array_1["top_2"], image_array_2["down_1"],image_array_2["down_2"])
        # one_structure = oneRowStructureSimilarity(image_1, image_2)
        # two_structure = twoRowsStructureSimilarity(image_1, image_2)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

    # second image at down x = 0, y = 1, compare down from image 1, and top from image 2
    if image_1_x == image_2_x and image_1_y < image_2_y:
        print("Check down adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["down_1"], image_array_2["top_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["down_1"], image_array_1["down_2"], image_array_2["top_1"],image_array_2["top_2"])
        # one_structure = oneRowStructureSimilarity(image_2, image_1)
        # two_structure = twoRowsStructureSimilarity(image_2, image_1)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

    # second image at left x = -1, y = 0, left from image 1, right from image 2
    if image_1_x > image_2_x and image_1_y == image_2_y:
        print("Check left adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["left_1"], image_array_2["right_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["left_1"], image_array_1["left_2"], image_array_2["right_1"],image_array_2["right_2"])
        # one_structure = oneColumnStructureSimilarity(image_1, image_2)
        # two_structure = twoRowsStructureSimilarity(image_1, image_2)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

    # second image at right x = 1, y = 0, right from image 1, left from image 2
    if image_1_x < image_2_x and image_1_y == image_2_y:
        print("Check right adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["right_1"], image_array_2["left_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["right_1"], image_array_1["right_2"], image_array_2["left_1"],image_array_2["left_2"])
        # one_structure = oneColumnStructureSimilarity(image_2, image_1)
        # two_structure = twoRowsStructureSimilarity(image_2, image_1)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

    # if similarity > SIMILARITY_THRESHOLDS:
    #     isAdjacent = True


    if one_similarity > SIMILARITY_THRESHOLDS:
        isAdjacent = True

    return isAdjacent

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
        DisplayImage(image_path, TILE_SIZE)
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
