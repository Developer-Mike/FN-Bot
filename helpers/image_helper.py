import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO

import constants

def from_url(url, size=512, mode='RGBA'):
    try:
        response = requests.get(f"{url}?width={size}", stream=True)

        image = Image.open(BytesIO(response.content))
        return image.convert(mode).resize((size, size), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Error: {url} is not a valid image.")

        if not constants.CONTINUE_ON_CORRUPTED_IMAGE or (not isinstance(e, UnidentifiedImageError) and not isinstance(e, requests.exceptions.MissingSchema)):
            raise e

        return Image.new(mode, (size, size), (0, 0, 0, 0))

def from_path(path, size=512):
    image = Image.open(path).convert('RGBA')

    if size > 0:
        return image.resize((size, size), Image.Resampling.LANCZOS)
    else:
        return image