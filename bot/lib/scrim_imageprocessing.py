import cv2
import numpy as np
from PIL import Image

def greyscale_image(image: Image.Image) -> Image.Image:
    """
    Convert an image to greyscale.
    """
    return image.convert("L")

def binarize_image(image: Image.Image) -> Image.Image:
    image = greyscale_image(image)
    image = np.array(image)
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(image)
    
def denoise_image(image: Image.Image) -> Image.Image:
    image = np.array(image)
    image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    return Image.fromarray(image)

def sharpen_image(image: Image.Image) -> Image.Image:
    image = np.array(image.convert('L'))
    sharpening_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return Image.fromarray(cv2.filter2D(image, -1, sharpening_kernel))

def crop_image_from_bounding_box(image: Image.Image, bounding_box: list) -> Image.Image:
    """
    Crop an image from a bounding box. The list should be structured in the format of [[x, y], [x, y], [x, y], [x, y]].
    """
    # First we need to determine the highest and lowest points of the box
    x_values = [point[0] for point in bounding_box]
    y_values = [point[1] for point in bounding_box]
    x_min = min(x_values)
    x_max = max(x_values)
    y_min = min(y_values)
    y_max = max(y_values)
    # Now we can crop the image
    return image.crop((x_min, y_min, x_max, y_max))