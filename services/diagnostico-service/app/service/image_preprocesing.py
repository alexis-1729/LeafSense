import numpy as np
from PIL import Image

def preprocess_image(image: Image.Image, target_size=(128, 128)):
    image = image.resize(target_size)
    array = np.asarray(image) / 255.0
    return array
