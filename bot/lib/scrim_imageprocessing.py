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