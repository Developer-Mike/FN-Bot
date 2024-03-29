import requests, os, time
from PIL import Image, UnidentifiedImageError
from io import BytesIO

import constants

CORRUPTED_IMAGE_ERRORS = [OSError, UnidentifiedImageError, requests.exceptions.MissingSchema]

def _from_url_unsafe(url, size=512, mode='RGBA'):
    response = requests.get(f"{url}?width={size}", stream=True)

    image = Image.open(BytesIO(response.content))
    return image.convert(mode).resize((size, size), Image.Resampling.LANCZOS)

def from_url(url, size=512, mode='RGBA'):
    try: return _from_url_unsafe(url, size, mode)
    except Exception as e:
        print(f"Error: {url} is not a valid image.")

        if not (constants.CONTINUE_ON_CORRUPTED_IMAGE and type(e) in CORRUPTED_IMAGE_ERRORS):
            raise e

        return Image.new(mode, (size, size), (0, 0, 0, 0))
    
def get_item_image(url, item_id, size=512, mode='RGBA'):
    try: 
        return _from_url_unsafe(url, size, mode)
    except Exception as e:
        print(f"Error: {url} is not a valid image.")

        if not (constants.CONTINUE_ON_CORRUPTED_IMAGE and type(e) in CORRUPTED_IMAGE_ERRORS):
            raise e
        
        if constants.FALLBACK_IMAGE_FROM_FORTNITE_API:
            print("Using fallback image from fortnite-api.com")

            fallback_image_featured = f"https://fortnite-api.com/images/cosmetics/br/{item_id.lower()}/featured.png"
            try: return _from_url_unsafe(fallback_image_featured, size, mode)
            except:
                fallback_image_icon = f"https://fortnite-api.com/images/cosmetics/br/{item_id.lower()}/icon.png"
                try: return _from_url_unsafe(fallback_image_icon, size, mode)
                except: pass

        return Image.new(mode, (size, size), (0, 0, 0, 0))

def with_background(image, background):
    background = background.resize(image.size)
    background.paste(image, (0, 0), image)
    return background

def from_path(path, size=512):
    image = Image.open(path).convert('RGBA')

    if size > 0:
        return image.resize((size, size), Image.Resampling.LANCZOS)
    else:
        return image
    
def compress_image(image, save_path):
        image.save(save_path, optimize=True, quality=85)

        current_size = (image.width, image.height)
        size_step = 250
        size_limit = 3000000

        start_time = time.time()
        while os.path.getsize(save_path) > size_limit:
            image = image.resize(current_size, Image.Resampling.LANCZOS)
            image.save(save_path, optimize=True, quality=85)

            current_size[0] -= size_step
            current_size[1] -= size_step

        image.close() # Free memory
        print(f"Compressed image to {os.path.getsize(save_path)} bytes. Took {round(time.time() - start_time, 2)} seconds.")