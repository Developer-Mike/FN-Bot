import os, shutil, math, pickle, time, glob
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

from helpers import exception_helper, image_helper, request_helper, post_helper, strings_helper
import constants

class LeaksModule:
    _LEAKED_ITEM_IMAGE_SIZE = 512

    _LEAKS_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
    _TEMP_PATH = os.path.join(_LEAKS_MODULE_PATH, "temp")
    _RESULT_PATH = os.path.join(_LEAKS_MODULE_PATH, "result")
    _LAST_LEAKS_LIST_PATH = os.path.join(_LEAKS_MODULE_PATH, "last_leaks.p")

    _API_LEAKS_URL = "https://fortniteapi.io/v2/items/upcoming"

    def __init__(self):
        if not os.path.exists(self._RESULT_PATH):
            os.makedirs(self._RESULT_PATH)

    def register(self, schedule):
        schedule.every(30).minutes.do(self.update)
    
    @exception_helper.catch_exceptions()
    def update(self):
        leaks_json = request_helper.io_request(self._API_LEAKS_URL, {"fields": "id,name,type,images"})
        leaks_date = self._parse_leaks_date(leaks_json)
        new_items = self._get_newly_leaked_items(leaks_json)

        if len(new_items) > 0:
            print("New leaks detected!")

            self._generate_icons(leaks_json, new_items)
            self._merge_leaks(leaks_date)
            
            print("Leaks image generated successfully!")
            shutil.rmtree(self._TEMP_PATH)

            self._post_image(leaks_date)
            
            pickle.dump(new_items, open(self._LAST_LEAKS_LIST_PATH, "wb"))

    def _parse_leaks_date(self, leaks_json):
        return leaks_json['lastUpdate']['date'][:10]

    def _get_newly_leaked_items(self, leaks_json):
        last_leaks = (pickle.load(open(self._LAST_LEAKS_LIST_PATH, "rb")) 
                    if os.path.exists(self._LAST_LEAKS_LIST_PATH)
                        else [])
        
        new_leaks = []
        for item_json in leaks_json['items']:
            item_id = item_json['id']

            if item_id not in last_leaks:
                new_leaks.append(item_id)

        return new_leaks 

    def _generate_icons(self, leaks_json, new_items):
        leak_items = leaks_json['items']

        # Create temp folder
        if os.path.exists(self._TEMP_PATH):
            shutil.rmtree(self._TEMP_PATH)
        os.mkdir(self._TEMP_PATH)

        # Load assets
        overlay_image = image_helper.from_path(os.path.join(constants.ASSETS_PATH, 'overlay.png'))
        new_badge = image_helper.from_path(os.path.join(constants.ASSETS_PATH, "new_badge.png"))

        for leak_item in leak_items:
            item_id = leak_item['id']
            if item_id not in new_items:
                continue

            # Item Image
            item_background_url = leak_item['images']['background']
            icon_image = image_helper.from_url(item_background_url, mode='RGB')

            #Overlay
            icon_image.paste(overlay_image, (0, 0), overlay_image)

            # Item Name
            item_name = leak_item['name']
            #Smaller text to fit image
            font = None
            font_size = 45
            while font is None or font.getlength(item_name) > 450:
                font = ImageFont.truetype(constants.FONT_PATH, font_size)
                font_size -= 2
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 423), item_name.upper(), font=font, fill='white', anchor='ms')

            # Item Type
            type_text = leak_item['type']['name']
            #Smaller text to fit image
            font = None
            font_size = 30
            while font is None or font.getlength(item_name) > 450:
                font = ImageFont.truetype(constants.FONT_PATH, font_size)
                font_size -= 2
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 460), type_text, font=font, fill=(255, 255, 255), anchor='ms')

            # Item Price
            font = ImageFont.truetype(constants.FONT_PATH, 40)
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 505), "???", font=font, fill='white', anchor='ms')

            #Save image
            icon_image.save(os.path.join(self._TEMP_PATH, f'{item_id}.png'))
            icon_image.close()

        # Free memory
        overlay_image.close()
        new_badge.close()

        print(f'Generated images for {len(new_items)} new leaks.')

    def _merge_leaks(self, leaks_date):
        leaks_images_paths = []
        for filepath in os.listdir(self._TEMP_PATH):
            leaks_images_paths.append(os.path.join(self._TEMP_PATH, filepath))
        leaks_count = len(leaks_images_paths)
            
        column_count = math.ceil(math.sqrt(leaks_count))
        leaks_image_size = self._LEAKED_ITEM_IMAGE_SIZE * column_count

        leaks_image = Image.new("RGB", (leaks_image_size, leaks_image_size))
        leaks_background = Image.open(os.path.join(constants.ASSETS_PATH, "background.png")).convert("RGB").resize((leaks_image_size, leaks_image_size))
        leaks_image.paste(leaks_background, (0, 0))
        leaks_background.close() # Free memory

        for i, leaks_image_path in enumerate(sorted(leaks_images_paths)):
            item_image = image_helper.from_path(leaks_image_path, size=self._LEAKED_ITEM_IMAGE_SIZE)
            leaks_image.paste(
                item_image,
                ((0 + ((i % column_count) * item_image.width)),
                    (0 + ((i // column_count) * item_image.height)))
            )
            item_image.close() # Free memory
        
        #Credits
        try:
            credit_images = glob.glob(os.path.join(constants.ASSETS_PATH, "ads/*.png"))
            spare_cells = column_count ** 2 - leaks_count
            for i in range(spare_cells):
                if i >= len(credit_images):
                    continue

                credits_image = image_helper.from_path(credit_images[i], size=self._LEAKED_ITEM_IMAGE_SIZE)
                leaks_image.paste(credits_image, (leaks_image_size - self._LEAKED_ITEM_IMAGE_SIZE * (i + 1), leaks_image_size - self._LEAKED_ITEM_IMAGE_SIZE), credits_image)
                credits_image.close() # Free memory
        except Exception as e:
            print(f"Error generating credits ({e})")
        
        leaks_image.save(os.path.join(self._RESULT_PATH, f'leaks_{leaks_date}.jpg'), optimize=True, quality=85)

    def _post_image(self, leaks_date):
        split_date = leaks_date.split('-')
        reformatted_date = f'{split_date[2]}/{split_date[1]}/{split_date[0]}'

        post_helper.post_image(
            os.path.join(self._RESULT_PATH, f'leaks_{leaks_date}.jpg'),
            strings_helper.STRINGS["leaks_post_caption"].replace('{date}', reformatted_date)
        )