from PIL import Image, ImageEnhance
import numpy as np

def preprocess(img: Image.Image, p: dict) -> Image.Image:
    img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(p.get("contrast", 1.0))
    img = ImageEnhance.Brightness(img).enhance(p.get("brightness", 1.0))
    img = ImageEnhance.Sharpness(img).enhance(p.get("sharpness", 1.0))

    if p.get("invert", False):
        img = Image.fromarray(255 - np.array(img))

    return img
