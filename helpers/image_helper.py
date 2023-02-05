import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO

def from_url(url, size=512, mode='RGBA'):
    response = requests.get(f"{url}?width={size}", stream=True)
    
    try: 
        image = Image.open(BytesIO(response.content))
        return image.convert(mode).resize((size, size), Image.Resampling.LANCZOS)
    except UnidentifiedImageError:
        print(f"Error: {url} is not a valid image.")
        return Image.new(mode, (size, size), (0, 0, 0, 0))

def from_path(path, size=512):
    image = Image.open(path).convert('RGBA')

    if size > 0:
        return image.resize((size, size), Image.Resampling.LANCZOS)
    else:
        return image