from PIL import Image

def supersample_image(img: Image.Image, factor: int) -> Image.Image:
    if factor <= 1:
        return img

    w, h = img.size
    return img.resize((w * factor, h * factor), Image.BICUBIC)
