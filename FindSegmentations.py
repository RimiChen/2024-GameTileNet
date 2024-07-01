from DisplayImage import *


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


def SeparateObjects(image_path, tile_size):
    # matrix = [
    #     [1, 0, 2, 2, 2],
    #     [1, 1, 0, 2, 0],
    #     [0, 1, 0, 1, 0],
    #     [3, 0, 1, 1, 0],
    #     [3, 0, 1, 1, 1],
    #     [3, 3, 0, 2, 2]
    # ]
    
    tile_map_image = Image.open(image_path)   
    width, height = tile_map_image.size
    x_max = math.floor(width/tile_size)
    y_max = math.floor(height/tile_size)
    print("x: {x_max}, {y_max}")

    # rows, cols = len(matrix), len(matrix[0])
    # x = 0
    # y = 0
    # unvisited_index = {}
    # for x in range(cols):
    #     for y in range(rows):
    #         index = getName(x, y)
    #         if index not in unvisited_index:
    #             unvisited_index[index] = matrix[y][x]
    
    # # print(unvisited_index)
    # visited = {}



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

if __name__ == "__main__":
    # main()

    tileset_folder = "Data/GameTile/Tilesets/"
    tileset_name = "001_001.png"
    tile_size = 32

    DisplayImage(tileset_folder+tileset_name, 32)
    SeparateObjects(tileset_folder+tileset_name)