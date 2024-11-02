import requests
from PIL import Image
from io import BytesIO
import base64


def load_image(path: str) -> Image.Image:
    """
    Load an image from a given path.

    Args:
        path (str): The path to the image to load.

    Returns:
        Image.Image: The downloaded image as a PIL Image object.
    """
    return Image.open(path)


def resize_image(image: Image.Image, max_size: int) -> Image.Image:
    """
    Resize an image while maintaining its aspect ratio.

    Args:
        image (Image.Image): The image to resize.
        max_size (int): The maximum size for either width or height.

    Returns:
        Image.Image: The resized image.
    """
    ratio = max_size / max(image.size)
    new_size: tuple[int, int] = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """
    Convert a PIL Image to a base64 encoded string.

    Args:
        image (Image.Image): The image to convert.
        format (str): The format to save the image as. Default is 'JPEG'.

    Returns:
        str: The base64 encoded string of the image.
    """
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def process_image(path: str, max_size: int = 1920) -> str:
    """
    Download an image or GIF, resize it, and return it as a base64 encoded string.
    For GIFs, it extracts a frame from the middle.

    Args:
        path (str): The path to the image to process.
        max_size (int): The maximum size for either width or height. Default is 800.

    Returns:
        str: The base64 encoded string of the processed image.
    """
    image = load_image(path)

    if getattr(image, "is_animated", False):
        frame_index = 0
        image.seek(frame_index)
        image = image.convert("RGB")

    resized_image = resize_image(image, max_size)
    f = "JPEG" if resized_image.mode == "RGB" else "PNG"
    base64_image = image_to_base64(resized_image, format=f)
    return f"{base64_image}"
