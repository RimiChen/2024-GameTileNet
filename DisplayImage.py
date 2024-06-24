from PIL import Image
import numpy as np
import math
from pathlib import Path
import matplotlib.pyplot as plt

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