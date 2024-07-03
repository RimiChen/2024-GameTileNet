import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from collections import Counter



def is_row_alpha_mostly_zero(image, row_index, threshold=0.85):
    """
    Check if a specific row in an image has alpha values that are mostly 0.

    Parameters:
    image (PIL.Image.Image): The image object.
    row_index (int): The index of the row to check.
    threshold (float): Fraction of pixels in the row that need to have alpha value 0 for the row to be considered mostly transparent.

    Returns:
    bool: True if the row's alpha values are mostly 0, False otherwise.
    """
    pixels = image.load()
    width = image.width
    alpha_values = [pixels[x, row_index][3] for x in range(width)]
    
    # Count the occurrences of each alpha value in the row
    alpha_counter = Counter(alpha_values)
    zero_alpha_count = alpha_counter[0]
    
    # Calculate the fraction of pixels with alpha value 0
    zero_alpha_fraction = zero_alpha_count / width

    return zero_alpha_fraction >= threshold

def is_column_alpha_mostly_zero(image, column_index, threshold=0.85):
    """
    Check if a specific column in an image has alpha values that are mostly 0.

    Parameters:
    image (PIL.Image.Image): The image object.
    column_index (int): The index of the column to check.
    threshold (float): Fraction of pixels in the column that need to have alpha value 0 for the column to be considered mostly transparent.

    Returns:
    bool: True if the column's alpha values are mostly 0, False otherwise.
    """
    pixels = image.load()
    height = image.height
    alpha_values = [pixels[column_index, y][3] for y in range(height)]
    
    # Count the occurrences of each alpha value in the column
    alpha_counter = Counter(alpha_values)
    zero_alpha_count = alpha_counter[0]
    
    # Calculate the fraction of pixels with alpha value 0
    zero_alpha_fraction = zero_alpha_count / height

    return zero_alpha_fraction >= threshold

def is_image_mostly_blank(image_path, threshold=0.85):
    """
    Check if an image is mostly blank (threshold% of the pixels are the same color).

    Parameters:
    image_path (str): Path to the image file.
    threshold (float): Fraction of pixels that need to be the same for the image to be considered blank.

    Returns:
    bool: True if the image is mostly blank, False otherwise.
    """
    image = Image.open(image_path).convert("RGBA")
    pixels = image.getdata()
    pixel_count = len(pixels)
    
    # Count the occurrences of each pixel
    pixel_counter = Counter(pixels)
    most_common_pixel_count = pixel_counter.most_common(1)[0][1]

    # Calculate the fraction of the most common pixel
    most_common_fraction = most_common_pixel_count / pixel_count

    return most_common_fraction >= threshold

def is_almost_transparent(image_path, threshold=0.95, alpha_threshold=10):
    """
    Check if an image is almost transparent.

    Args:
    image_path (str): Path to the image file.
    threshold (float): Proportion of transparent pixels required to consider the image almost transparent.
                       Default is 0.95 (i.e., 95% transparent pixels).
    alpha_threshold (int): Maximum alpha value to consider a pixel as transparent.
                           Default is 10 (on a scale of 0-255).

    Returns:
    bool: True if the image is almost transparent, False otherwise.
    """
    with Image.open(image_path) as img:
        # Convert the image to RGBA if it does not have an alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert the image to a NumPy array
        img_array = np.array(img)
        
        # Get the alpha channel
        alpha_channel = img_array[:, :, 3]
        
        # Count the number of almost transparent pixels
        transparent_pixels = np.sum(alpha_channel <= alpha_threshold)
        
        # Calculate the proportion of almost transparent pixels
        total_pixels = alpha_channel.size
        transparent_proportion = transparent_pixels / total_pixels
        
        # Determine if the image is almost transparent
        return transparent_proportion >= threshold

# check an image is blank
def is_image_blank(image_path):
    """
    Check if an image is blank (single color or transparent).

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    bool: True if the image is blank, False otherwise.
    """
    image = Image.open(image_path).convert("RGBA")
    pixels = image.getdata()

    # Get the first pixel value
    first_pixel = pixels[0]

    # Check if all pixels are the same as the first pixel
    for pixel in pixels:
        if pixel != first_pixel:
            return False
    return True

# get image index from image path
def get_image_index(image_path):
    image_name = Path(image_path).stem
    name_array = image_name.split("_")
    last_two = name_array[-2:]
    image_x_index = last_two[0]
    image_y_index = last_two[1]
    print("x, y = ", image_x_index, image_y_index)

    return image_x_index, image_y_index


def is_row_almost_empty(image, row_index, threshold=0.85):
    """
    Check if a specific row in an image is almost empty.

    Parameters:
    image (PIL.Image.Image): The image object.
    row_index (int): The index of the row to check.
    threshold (float): Fraction of pixels in the row that need to be the same for the row to be considered almost empty.

    Returns:
    bool: True if the row is almost empty, False otherwise.
    """
    pixels = image.load()
    width = image.width
    row_pixels = [pixels[x, row_index] for x in range(width)]
    
    # Count the occurrences of each pixel value in the row
    pixel_counter = Counter(row_pixels)
    most_common_pixel_count = pixel_counter.most_common(1)[0][1]
    
    # Calculate the fraction of the most common pixel value in the row
    most_common_fraction = most_common_pixel_count / width

    return most_common_fraction >= threshold

def is_column_almost_empty(image, column_index, threshold=0.85):
    """
    Check if a specific column in an image is almost empty.

    Parameters:
    image (PIL.Image.Image): The image object.
    column_index (int): The index of the column to check.
    threshold (float): Fraction of pixels in the column that need to be the same for the column to be considered almost empty.

    Returns:
    bool: True if the column is almost empty, False otherwise.
    """
    pixels = image.load()
    height = image.height
    column_pixels = [pixels[column_index, y] for y in range(height)]
    
    # Count the occurrences of each pixel value in the column
    pixel_counter = Counter(column_pixels)
    most_common_pixel_count = pixel_counter.most_common(1)[0][1]
    
    # Calculate the fraction of the most common pixel value in the column
    most_common_fraction = most_common_pixel_count / height

    return most_common_fraction >= threshold

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



def checkSimilarity(image_path_1, image_path_2):
    isAdjacent = False
    # connect_directions = []
    image_1 = Image.open(image_path_1).convert('RGBA')
    image_1_w, image_1_h = image_1.size
    image_2 = Image.open(image_path_2).convert('RGBA')
    image_2_w, image_2_h = image_2.size
    # plt.imshow(image_1)
    # plt.show()    
    # plt.imshow(image_2)
    # plt.show()    

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
        similarity = one_similarity
        if is_row_alpha_mostly_zero(image_1, 0) or is_row_alpha_mostly_zero(image_2, image_2_h-1):
        # if is_row_almost_empty(image_1, 0) or is_row_almost_empty(image_2, image_2_h-1):
            print("image 2 at top, Separate Images because of empty row")
            similarity = 0.0

    # second image at down x = 0, y = 1, compare down from image 1, and top from image 2
    if image_1_x == image_2_x and image_1_y < image_2_y:
        print("Check down adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["down_1"], image_array_2["top_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["down_1"], image_array_1["down_2"], image_array_2["top_1"],image_array_2["top_2"])
        # one_structure = oneRowStructureSimilarity(image_2, image_1)
        # two_structure = twoRowsStructureSimilarity(image_2, image_1)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  
        
        similarity = one_similarity
        if is_row_alpha_mostly_zero(image_1, image_1_h-1) or is_row_alpha_mostly_zero(image_2, 0):
        # if is_row_almost_empty(image_1, image_1_h-1) or is_row_almost_empty(image_2, 0):
            print("image 2 at down, Separate Images because of empty row")
            similarity = 0.0


    # second image at left x = -1, y = 0, left from image 1, right from image 2
    if image_1_x > image_2_x and image_1_y == image_2_y:
        print("Check left adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["left_1"], image_array_2["right_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["left_1"], image_array_1["left_2"], image_array_2["right_1"],image_array_2["right_2"])
        # one_structure = oneColumnStructureSimilarity(image_1, image_2)
        # two_structure = twoRowsStructureSimilarity(image_1, image_2)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

        similarity = one_similarity
        if is_column_alpha_mostly_zero(image_1, 0) or is_column_alpha_mostly_zero(image_2, image_2_w -1):        
        # if is_column_almost_empty(image_1, 0) or is_row_almost_empty(image_2, image_2_w -1):
            print("image 2 at left, Separate Images because of empty column")
            similarity = 0.0

    # second image at right x = 1, y = 0, right from image 1, left from image 2
    if image_1_x < image_2_x and image_1_y == image_2_y:
        print("Check right adjacency")
        one_similarity = oneLineColorSimilarity(image_array_1["right_1"], image_array_2["left_1"])
        two_similarity = twoLineColorSimilarity(image_array_1["right_1"], image_array_1["right_2"], image_array_2["left_1"],image_array_2["left_2"])
        # one_structure = oneColumnStructureSimilarity(image_2, image_1)
        # two_structure = twoRowsStructureSimilarity(image_2, image_1)
        # print("one line color: ", one_similarity, "two lines color: ", two_similarity, "one_structure: ", one_structure, "two_structure: ", two_structure)  
        print("one line color: ", one_similarity, "two lines color: ", two_similarity)  

        similarity = one_similarity
        if is_column_alpha_mostly_zero(image_1, image_1_w -1) or is_column_alpha_mostly_zero(image_2, 0):   
        # if is_column_almost_empty(image_1, image_1_w -1) or is_row_almost_empty(image_2, 0):
            print("image 2 at right, Separate Images because of empty column")
            similarity = 0.0

    # if similarity > SIMILARITY_THRESHOLDS:
    #     isAdjacent = True


    # if one_similarity > SIMILARITY_THRESHOLDS:
    #     isAdjacent = True

    return similarity