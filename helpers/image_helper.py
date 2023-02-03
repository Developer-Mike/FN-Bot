import requests
from PIL import Image
from io import BytesIO

def from_url(url, size=512):
    response = requests.get(f"{url}?width={size}", stream=True)
    image = Image.open(BytesIO(response.content))
    
    return image.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)

def from_path(path, size=512):
    image = Image.open(path).convert('RGBA')

    if size > 0:
        return image.resize((size, size), Image.Resampling.LANCZOS)
    else:
        return image