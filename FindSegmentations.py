from DisplayImage import *
import os
from CheckTileSimilarity import *
from PIL import Image
from CreateFileList import *

tile_name = "tiles_"
format = ".png"
Similarity_threshold = 0.671875
image_folder = "Data/GameTile/small_dataset/"
out_path = "Data/GameTile/Json/"
out_file = out_path+"all_tilesets.json"

### get image name from image path
def getImageName(image_path):
    # image_name = os.path.basename(image_path)
    image_name = Path(image_path).stem
    # print(image_name)
    return image_name

def getName(x, y):
    return str(x)+"_"+str(y)
def getXY(name):
    name_array = name.split("_")
    return int(name_array[0]), int(name_array[1]) 

def check_segment(matrix, x, y, visited, area, unvisited_index, parent):
    rows, cols = len(matrix), len(matrix[0])
    print(rows, cols)
   
    # Boundary and value check
    if y >= rows or x >= cols:
        print("our of index", (x,y))
        # del unvisited_index[getName(x,y)]
        return
    else:
        print("check ", (x,y), matrix[y][x])
        ### record as visited and delete from seed list
        if matrix[y][x] not in visited:
            visited[getName(x,y)] = 1

        else:
            if visited[getName(x,y)] == 1:
                print("was visited ", (x,y))

        del unvisited_index[getName(x,y)]    
    # if alpha == 0
    if matrix[y][x] == 0:
        print("0, delete", (x, y))
        # del unvisited_index[getName(x,y)]
        return
    else: # not 0
        if parent == "":
            # no parent, mean it is the seed
            print("this is seed ", (x,y))
            parent = getName(x, y)
            area[parent] = []
        else:
            pass

    if parent not in area[parent]:
        area[parent].append(getName(x,y)) 
    if getName(x,y) not in area[parent]:
        area[parent].append(getName(x,y))     


    
    # check right
    if x+1 < cols:
        print((x,y), "check right", (x+1, y))
        if matrix[y][x+1] == matrix[y][x]  and matrix[y][x] != 0 and getName(x+1, y) not in visited:

            check_segment(matrix, x+1, y, visited, area, unvisited_index, parent)
        else:
            # del unvisited_index[getName(x+1,y)]
            pass
    # check left
    if x-1 >= 0:
        print((x,y), "check left", (x-1, y))
        if matrix[y][x-1] == matrix[y][x]  and matrix[y][x] != 0 and getName(x-1, y) not in visited:
            check_segment(matrix, x-1, y, visited, area, unvisited_index, parent)
        else:
            # del unvisited_index[getName(x+1,y)]
            pass

    # check down
    if y+1 < rows:
        print((x,y), "check", (x, y+1))
        # if getName(x,y) not in area[parent]:
        #     area[parent].append(getName(x,y))

        if  matrix[y+1][x]== matrix[y][x] and matrix[y][x] != 0 and getName(x, y+1) not in visited:
            check_segment(matrix, x, y+1, visited, area, unvisited_index, parent)
        else:
            pass
            # del unvisited_index[getName(x,y+1)]       
    # check top
    if y-1 >= 0:
        print((x,y), "check", (x, y-1))
        # if getName(x,y) not in area[parent]:
        #     area[parent].append(getName(x,y))

        if  matrix[y-1][x]== matrix[y][x] and matrix[y][x] != 0 and getName(x, y-1) not in visited:
            check_segment(matrix, x, y-1, visited, area, unvisited_index, parent)
        else:
            pass
            # del unvisited_index[getName(x,y+1)]  

    # Mark as visited and add to area

    return

def main():
    matrix = [
        [1, 0, 2, 2, 2],
        [1, 1, 0, 2, 0],
        [0, 1, 0, 1, 0],
        [3, 0, 1, 1, 0],
        [3, 0, 1, 1, 1],
        [3, 3, 0, 2, 2]
    ]
    
    rows, cols = len(matrix), len(matrix[0])
    x = 0
    y = 0
    unvisited_index = {}
    for x in range(cols):
        for y in range(rows):
            index = getName(x, y)
            if index not in unvisited_index:
                unvisited_index[index] = matrix[y][x]
    
    # print(unvisited_index)
    visited = {}



    # visited = [[False for _ in range(len(matrix[0]))] for _ in range(len(matrix))]

    start_x, start_y = 0, 0  # Starting point
    # if matrix[start_x][start_y] == 1:
    area = {}
    while len(unvisited_index) > 0 :
        print(unvisited_index) 
        start_x, start_y = getXY(next(iter(unvisited_index)))
        print("new seed ", (start_x, start_y))
        parent = ""
        check_segment(matrix, start_x, start_y, visited, area, unvisited_index, parent)
    
        # Report the list of adjacent areas
        print("Adjacent area:", area)

def check_png_file_exists(file_path):
    """
    Check whether a PNG file exists at the specified file path.
    
    Args:
    file_path (str): The path to the PNG file.
    
    Returns:
    bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path) and file_path.lower().endswith('.png')

# def get_image_folder_path():

#     return image_folder+ getImageName(image_name)+ "_no_reduce/"+ image_name
def chekcAdjacent(image1_path, image2_path):
    if checkSimilarity(image1_path, image2_path) >= Similarity_threshold:
        return True
    else:
        return False

def check_segment_for_tiles(target_folder, x_max, y_max, x, y, visited, area, unvisited_index, image_path_dictionary, parent):
    rows, cols = y_max, x_max
    print("rows = ", rows, "cols = ", cols)



    # Boundary and value check
    if y >= rows or x >= cols:
        print("our of index", (x,y))
        # del unvisited_index[getName(x,y)]
        return
    else:

        print("check ", (x,y))
        new_index = getName(x,y)
        # print(new_index)
        image1_path = image_path_dictionary[new_index]
        # print(image1_path)

        ### record as visited and delete from seed list
        if new_index not in visited:
            visited[new_index] = 1

        else:
            if visited[new_index] == 1:
                print("was visited ", (x,y))

        del unvisited_index[new_index]    
    # if alpha == 0

# is_image_mostly_blank(new_path):
#             # if an blank image
#             os.remove(new_path)
    if is_almost_transparent(image1_path) == True:
    # if is_image_mostly_blank(image1_path) == True:
        print("0, delete", (x, y))
        # del unvisited_index[getName(x,y)]
        return
    else: # not 0
        if parent == "":
            # no parent, mean it is the seed
            print("this is seed ", (x,y))
            parent = getName(x, y)
            area[parent] = []
        else:
            pass

    if parent not in area[parent]:
        area[parent].append(getName(x,y)) 
    if getName(x,y) not in area[parent]:
        area[parent].append(getName(x,y))     


    
    # check right
    if x+1 < cols:
        print("rows = ", rows, "cols = ", cols)
        print((x,y), "check right", (x+1, y))
        # if matrix[y][x+1] == matrix[y][x]  and matrix[y][x] != 0 and getName(x+1, y) not in visited:
        image2_path = image_path_dictionary[getName(x+1, y)]
        # if chekcAdjacent(image1_path, image2_path) == True and is_image_mostly_blank(image1_path) == False and getName(x+1, y) not in visited:
        if chekcAdjacent(image1_path, image2_path) == True and is_almost_transparent(image1_path) == False and getName(x+1, y) not in visited:

            # check_segment(matrix, x+1, y, visited, area, unvisited_index, parent)
            check_segment_for_tiles(target_folder, x_max, y_max, x+1, y, visited, area, unvisited_index, image_path_dictionary, parent)
        else:
            # del unvisited_index[getName(x+1,y)]
            pass
    # check left
    if x-1 >= 0:
        print("rows = ", rows, "cols = ", cols)
        print((x,y), "check left", (x-1, y))
        image2_path = image_path_dictionary[getName(x-1, y)]
        # if chekcAdjacent(image1_path, image2_path) == True  and is_image_mostly_blank(image1_path) == False and getName(x-1, y) not in visited:
        if chekcAdjacent(image1_path, image2_path) == True  and is_almost_transparent(image1_path) == False and getName(x-1, y) not in visited:
            # check_segment(matrix, x-1, y, visited, area, unvisited_index, parent)
            check_segment_for_tiles(target_folder, x_max, y_max, x-1, y, visited, area, unvisited_index, image_path_dictionary, parent)
        else:
            # del unvisited_index[getName(x+1,y)]
            pass

    # check down
    if y+1 < rows:
        print("rows = ", rows, "cols = ", cols)
        print((x,y), "check", (x, y+1))
        # if getName(x,y) not in area[parent]:
        #     area[parent].append(getName(x,y))

        # if  matrix[y+1][x]== matrix[y][x] and matrix[y][x] != 0 and getName(x, y+1) not in visited:
        image2_path = image_path_dictionary[getName(x, y+1)]
        # if  chekcAdjacent(image1_path, image2_path) == True  and is_image_mostly_blank(image1_path) == False and getName(x, y+1) not in visited:
        if  chekcAdjacent(image1_path, image2_path) == True  and is_almost_transparent(image1_path) == False and getName(x, y+1) not in visited:
            # check_segment(matrix, x, y+1, visited, area, unvisited_index, parent)
            check_segment_for_tiles(target_folder, x_max, y_max, x, y+1, visited, area, unvisited_index, image_path_dictionary, parent)
        else:
            pass
            # del unvisited_index[getName(x,y+1)]       
    # check top
    if y-1 >= 0:
        print("rows = ", rows, "cols = ", cols)
        print((x,y), "check", (x, y-1))
        # if getName(x,y) not in area[parent]:
        #     area[parent].append(getName(x,y))
        # if  matrix[y-1][x]== matrix[y][x] and matrix[y][x] != 0 and getName(x, y-1) not in visited:
        image2_path = image_path_dictionary[getName(x, y-1)]
        # if  chekcAdjacent(image1_path, image2_path) == True  and is_image_mostly_blank(image1_path) == False and getName(x, y-1) not in visited:
        if  chekcAdjacent(image1_path, image2_path) == True  and is_almost_transparent(image1_path) == False and getName(x, y-1) not in visited:
        # if  matrix[y-1][x]== matrix[y][x] and matrix[y][x] != 0 and getName(x, y-1) not in visited:
            # check_segment(matrix, x, y-1, visited, area, unvisited_index, parent)
            check_segment_for_tiles(target_folder, x_max, y_max, x, y-1, visited, area, unvisited_index, image_path_dictionary, parent)
        else:
            pass
            # del unvisited_index[getName(x,y+1)]  

    # Mark as visited and add to area

    return


def SeparateObjects(image_folder, image_name, target_folder, tile_size):
    # matrix = [
    #     [1, 0, 2, 2, 2],
    #     [1, 1, 0, 2, 0],
    #     [0, 1, 0, 1, 0],
    #     [3, 0, 1, 1, 0],
    #     [3, 0, 1, 1, 1],
    #     [3, 3, 0, 2, 2]
    # ]
    
    tile_map_image = Image.open(image_folder+image_name)   
    width, height = tile_map_image.size
    x_max = math.floor(width/tile_size)
    y_max = math.floor(height/tile_size)
    print(width, height)
    print("x: ", x_max, y_max)


    rows, cols = y_max, x_max
    x = 0
    y = 0
    unvisited_index = {}
    image_path_dictionary = {}
    for x in range(cols):
        for y in range(rows):
            index = getName(x, y)
            if index not in unvisited_index:

                unvisited_index[index] = tile_name + index + format
                image_path_dictionary[index] = target_folder + tile_name + index + format
                new_image_path = target_folder + unvisited_index[index]
                isExist = check_png_file_exists(new_image_path)
                # print("image path = ", index,  unvisited_index[index], isExist, new_image_path)
                

    # print(unvisited_index)
    visited = {}

    start_x, start_y = 0, 0  # Starting point
    # if matrix[start_x][start_y] == 1:
    area = {}
    while len(unvisited_index) > 0 :
        # print(unvisited_index) 
        start_x, start_y = getXY(next(iter(unvisited_index)))
        print("new seed ", (start_x, start_y))
        parent = ""
        check_segment_for_tiles(target_folder, x_max, y_max, start_x, start_y, visited, area, unvisited_index, image_path_dictionary, parent)
    
        # Report the list of adjacent areas
        print("Adjacent area:", area)

    
    input_image_folder = target_folder
    output_folder = create_segmented_folder(target_folder)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    combine_images(area, input_image_folder, output_folder)



def combine_images(input_dict, image_folder, output_folder):
    for seed, neighbors in input_dict.items():
        images = []
        # Load all images
        for tile in neighbors:
            tile_path = os.path.join(image_folder, f'tiles_{tile}.png')
            if os.path.exists(tile_path):
                images.append((tile, Image.open(tile_path)))
        
        if not images:
            continue
        
        # Determine the bounding box for the combined image
        x_coords = [int(tile.split('_')[0]) for tile, _ in images]
        y_coords = [int(tile.split('_')[1]) for tile, _ in images]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        tile_size = images[0][1].size  # Assuming all tiles are the same size
        combined_width = (max_x - min_x + 1) * tile_size[0]
        combined_height = (max_y - min_y + 1) * tile_size[1]
        
        # Create a blank canvas for the combined image
        combined_image = Image.new('RGBA', (combined_width, combined_height))
        
        # Paste each image in the correct location
        for tile, img in images:
            x, y = map(int, tile.split('_'))
            x_offset = (x - min_x) * tile_size[0]
            y_offset = (y - min_y) * tile_size[1]
            combined_image.paste(img, (x_offset, y_offset))
        
        # Save the combined image
        output_path = os.path.join(output_folder, f'combined_{seed}.png')
        combined_image.save(output_path)
        print(f'Saved combined image for {seed} at {output_path}')



    # # visited = [[False for _ in range(len(matrix[0]))] for _ in range(len(matrix))]

    # start_x, start_y = 0, 0  # Starting point
    # # if matrix[start_x][start_y] == 1:
    # area = {}
    # while len(unvisited_index) > 0 :
    #     print(unvisited_index) 
    #     start_x, start_y = getXY(next(iter(unvisited_index)))
    #     print("new seed ", (start_x, start_y))
    #     parent = ""
    #     check_segment(matrix, start_x, start_y, visited, area, unvisited_index, parent)
    
    #     # Report the list of adjacent areas
    #     print("Adjacent area:", area)

def create_segmented_folder(path):
    """
    Modify the given path by removing any trailing slashes and appending "_seg/".
    Create the new directory if it doesn't exist.

    Args:
    path (str): The original path.

    Returns:
    str: The modified path.
    """
    # Remove any trailing slashes from the path
    if path.endswith('/'):
        path = path.rstrip('/')
    
    # Append "_seg/" to the path
    new_path = path + "_seg/"
    
    # Create the new directory if it doesn't exist
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    
    return new_path


if __name__ == "__main__":
    # main()

    tileset_folder = "Data/GameTile/small_Tilesets/"
    target_folder = "Data/GameTile/small_dataset/"
    tileset_name = "000_001.png"
    tile_size = 32



    
    all_tile_json = out_file
    file_list = list_files_in_folder(tileset_folder)
    save_file_list_to_json(file_list, out_file)
    # save_file_list_to_json(tileset_folder, out_file)
    
    # DisplayImage(tileset_folder+tileset_name, 32)
    for new_image in file_list:
        print(tileset_folder)

        new_image_name = getImageName(new_image)+".png"
        image_folder_path = target_folder + getImageName(new_image_name)+"_full/"        
        SeparateObjects(tileset_folder, new_image_name, image_folder_path, 32)