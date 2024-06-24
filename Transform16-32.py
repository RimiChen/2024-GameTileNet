import os
from PIL import Image

image_path = "Data/GameTile/16/"
out_path = "Data/GameTile/Tilesets/"


def resize_image(input_path, output_path, scale_factor=2):
    """
    Resize the image by a given scale factor.

    Parameters:
    input_path (str): Path to the input image file.
    output_path (str): Path to save the output image file.
    scale_factor (float): Factor by which to scale the image.

    Returns:
    None
    """
    # Open the input image
    with Image.open(input_path) as img:
        # Calculate the new size
        new_size = (img.width * scale_factor, img.height * scale_factor)
        # Resize the image
        resized_img = img.resize(new_size, Image.NEAREST)
        # Save the output image
        resized_img.save(output_path)
        print(f"Image saved to {output_path}")

# Example usage
if __name__ == "__main__":
    input_folder = "Data/GameTile/16/"  # Replace with your input folder path
    output_folder = "Data/GameTile/Tilesets/"  # Replace with your output folder path

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.png'):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            resize_image(input_path, output_path, scale_factor=2)